import os
import json
import time
from youtube_transcript_api import YouTubeTranscriptApi
from google import genai

# ⚠️ ここにGemini APIキーを入れる
API_KEY = os.environ.get("GEMINI_API_KEY", "")
DATA_DIR = r"C:\Users\manab\pikuhami\youtube-radio-archive\scripts\data"
MAX_VIDEOS = 999

os.makedirs(DATA_DIR, exist_ok=True)
client = genai.Client(api_key=API_KEY)


def get_transcript(video_id):
    ytt = YouTubeTranscriptApi()
    transcript = ytt.fetch(video_id, languages=['ja'])
    return [{"start": t.start, "text": t.text} for t in transcript]


def format_segments(segments):
    return "\n".join([
        f"[{int(s['start']//3600):02d}:{int((s['start']%3600)//60):02d}:{int(s['start']%60):02d}] {s['text']}"
        for s in segments
    ])


def call_gemini(prompt):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    res = response.text.strip()
    if res.startswith("```"):
        res = res.split("```")[1]
        if res.startswith("json"):
            res = res[4:]
    return json.loads(res)


def summarize_chunk(segments_chunk):
    text = format_segments(segments_chunk)
    start_time = f"{int(segments_chunk[0]['start']//3600):02d}:{int((segments_chunk[0]['start']%3600)//60):02d}:{int(segments_chunk[0]['start']%60):02d}"
    end_time   = f"{int(segments_chunk[-1]['start']//3600):02d}:{int((segments_chunk[-1]['start']%3600)//60):02d}:{int(segments_chunk[-1]['start']%60):02d}"
    prompt = f"""以下は{start_time}〜{end_time}のラジオ番組の文字起こしです。
# 出力形式（JSON）
{{"time_range": "{start_time} - {end_time}", "sections": [{{"time_range": "開始-終了", "title": "セクション名", "description": "内容を2〜3文で"}}], "songs": [{{"time": "時間", "title": "曲名", "artist": "アーティスト名"}}]}}
# ルール
- sectionsは話題の切れ目で区切る（5〜10分ごと目安）
- songsはMCが曲紹介している箇所を探す、なければ空配列
- JSONのみ返す
# 文字起こし
{text}"""
    return call_gemini(prompt)


def summarize_full(all_sections):
    sections_text = "\n".join([f"{s['time_range']} {s['title']}：{s['description']}" for s in all_sections])
    prompt = f"""以下はラジオ番組の各セクションの要約です。全体のまとめを作ってください。
# 出力形式（JSON）
{{"topics": ["話題1", "話題2"], "summary": "放送全体のあらすじを400〜500文字で"}}
# セクション一覧
{sections_text}
JSONのみ返してください。"""
    return call_gemini(prompt)


# --- バッチ処理メイン ---
with open(r"C:\Users\manab\pikuhami\youtube-radio-archive\scripts\filtered_ids.txt") as f:
    all_ids = [line.strip() for line in f if line.strip()]

processed = 0
for video_id in all_ids:
    if processed >= MAX_VIDEOS:
        print(f"\n⛔ {MAX_VIDEOS}本に達したため停止")
        break

    summary_path = f"{DATA_DIR}/{video_id}_summary.json"
    if os.path.exists(summary_path):
        print(f"⏭️  スキップ: {video_id}")
        continue

    print(f"\n▶️  処理中({processed+1}): {video_id}")
    try:
        segments = get_transcript(video_id)
        chunks = []
        max_time = segments[-1]["start"]
        for start in range(0, int(max_time) + 1, 3600):
            chunk = [s for s in segments if start <= s["start"] < start + 3600]
            if chunk:
                chunks.append(chunk)

        all_sections, all_songs = [], []
        for i, chunk in enumerate(chunks):
            print(f"  チャンク {i+1}/{len(chunks)}...")
            result = summarize_chunk(chunk)
            all_sections.extend(result.get("sections", []))
            all_songs.extend(result.get("songs", []))
            time.sleep(4)  # 無料枠レート制限対策

        full = summarize_full(all_sections)
        final = {"sections": all_sections, "songs": all_songs, "topics": full["topics"], "summary": full["summary"]}

        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(final, f, ensure_ascii=False, indent=2)

        print(f"✅ 完了: {video_id}")
        processed += 1

    except Exception as e:
        print(f"❌ エラー({video_id}): {e}")
        continue

print(f"\n🎉 完了: {processed}本処理しました")