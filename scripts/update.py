import os
import re
import json
import time
from pathlib import Path
from urllib.request import urlopen, Request
from youtube_transcript_api import YouTubeTranscriptApi
from google import genai

# === 設定 ===
CHANNEL_ID = "UCzXARgBFSrU9stjHpHNmMBQ"  # @prohamburger1118 のチャンネルID
API_KEY = os.environ.get("GEMINI_API_KEY", "")
SCRIPTS_DIR = Path(__file__).parent
DATA_DIR = SCRIPTS_DIR / "data"
IDS_FILE = SCRIPTS_DIR / "filtered_ids.txt"
OUT_DIR = SCRIPTS_DIR.parent / "src" / "data"


DATA_DIR.mkdir(exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)
client = genai.Client(api_key=API_KEY)


# === YouTube から最新動画IDとタイトルを取得 ===
def fetch_latest_videos(channel_id, max_results=5):
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    xml = urlopen(req).read().decode()
    entries = re.findall(
        r'<yt:videoId>(.*?)</yt:videoId>.*?<title>(.*?)</title>',
        xml, re.DOTALL
    )
    return [(vid.strip(), title.strip()) for vid, title in entries[:max_results]]


# === 字幕取得 ===
def get_transcript(video_id):
    ytt = YouTubeTranscriptApi()
    transcript = ytt.fetch(video_id, languages=['ja'])
    return [{"start": t.start, "text": t.text} for t in transcript]


# === Gemini 呼び出し ===
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


def format_segments(segments):
    return "\n".join([
        f"[{int(s['start']//3600):02d}:{int((s['start']%3600)//60):02d}:{int(s['start']%60):02d}] {s['text']}"
        for s in segments
    ])


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


# === filtered_ids.txt の読み書き ===
def load_ids():
    if not IDS_FILE.exists():
        return []
    with open(IDS_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def save_ids(ids):
    with open(IDS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(ids))


# === videos.json の再生成 ===
def build_videos_json(ids, titles_map):
    # 既存 videos.json のタイトルを読み込み、引数で上書き（引数を優先）
    existing = load_titles_map()
    existing.update(titles_map)
    titles_map = existing

    summary_files = {p.stem.replace("_summary", ""): p for p in DATA_DIR.glob("*_summary.json")}
    videos = []
    for video_id in ids:
        title = titles_map.get(video_id, video_id)
        has_summary = video_id in summary_files
        summary_data = None
        if has_summary:
            with open(summary_files[video_id], "r", encoding="utf-8") as f:
                summary_data = json.load(f)
        videos.append({
            "id": video_id,
            "title": title,
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "has_summary": has_summary,
            "summary": summary_data
        })
    with open(OUT_DIR / "videos.json", "w", encoding="utf-8") as f:
        json.dump(videos, f, ensure_ascii=False, indent=2)
    print(f"✅ videos.json 生成完了: {len(videos)}本（要約あり {sum(1 for v in videos if v['has_summary'])}本）")


# === タイトルマップを既存 videos.json から読み込む ===
def load_titles_map():
    videos_path = OUT_DIR / "videos.json"
    if not videos_path.exists():
        return {}
    with open(videos_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {v["id"]: v["title"] for v in data}


# === メイン処理 ===
def main():
    print("🔍 最新動画を取得中...")
    latest = fetch_latest_videos(CHANNEL_ID, max_results=5)
    print(f"  取得: {[vid for vid, _ in latest]}")

    existing_ids = load_ids()
    titles_map = load_titles_map()

    # 新しい動画だけ先頭に追加
    new_videos = [(vid, title) for vid, title in latest if vid not in existing_ids]
    if not new_videos:
        print("✨ 新しい動画はありませんでした")
    else:
        for vid, title in new_videos:
            print(f"  新規追加: {vid} / {title}")
            titles_map[vid] = title
        new_ids = [vid for vid, _ in new_videos] + existing_ids
        save_ids(new_ids)
        existing_ids = new_ids

    # 未処理の動画だけ要約（新規追加分のみ対象）
    to_process = [
        vid for vid, _ in new_videos
        if not (DATA_DIR / f"{vid}_summary.json").exists()
        and not (DATA_DIR / f"{vid}_skip.json").exists()
    ]

    if not to_process:
        print("✨ 未処理の動画はありませんでした")
    else:
        print(f"\n📝 要約処理: {len(to_process)}本")
        for video_id in to_process:
            print(f"\n▶️  処理中: {video_id} / {titles_map.get(video_id, '')}")
            try:
                segments = get_transcript(video_id)
                max_time = segments[-1]["start"]
                chunks = []
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
                    time.sleep(4)

                full = summarize_full(all_sections)
                final = {
                    "sections": all_sections,
                    "songs": all_songs,
                    "topics": full["topics"],
                    "summary": full["summary"]
                }
                with open(DATA_DIR / f"{video_id}_summary.json", "w", encoding="utf-8") as f:
                    json.dump(final, f, ensure_ascii=False, indent=2)
                print(f"✅ 完了: {video_id}")

            except Exception as e:
                print(f"❌ エラー({video_id}): {e}")
                # 字幕なし等で処理不能な場合はスキップマークを保存（再処理しない）
                skip_path = DATA_DIR / f"{video_id}_skip.json"
                with open(skip_path, "w", encoding="utf-8") as f:
                    json.dump({"skipped": True, "reason": str(e)}, f, ensure_ascii=False)

    # videos.json を再生成
    print("\n🔨 videos.json を更新中...")
    build_videos_json(existing_ids, titles_map)


if __name__ == "__main__":
    main()