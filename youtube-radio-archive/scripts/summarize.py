import anthropic
import json

client = anthropic.Anthropic(api_key="xxx-xxx-xxx")

def format_segments(segments):
    return "\n".join([
        f"[{int(s['start']//3600):02d}:{int((s['start']%3600)//60):02d}:{int(s['start']%60):02d}] {s['text']}"
        for s in segments
    ])

def summarize_chunk(segments_chunk):
    """30分ごとのチャンクを要約"""
    text = format_segments(segments_chunk)
    start_time = f"{int(segments_chunk[0]['start']//3600):02d}:{int((segments_chunk[0]['start']%3600)//60):02d}:{int(segments_chunk[0]['start']%60):02d}"
    end_time = f"{int(segments_chunk[-1]['start']//3600):02d}:{int((segments_chunk[-1]['start']%3600)//60):02d}:{int(segments_chunk[-1]['start']%60):02d}"

    prompt = f"""
以下は{start_time}〜{end_time}のラジオ番組の文字起こしです。

# 出力形式（JSON）
{{
  "time_range": "{start_time} - {end_time}",
  "sections": [
    {{
      "time_range": "開始時間 - 終了時間",
      "title": "セクション名",
      "description": "内容を2〜3文で"
    }}
  ],
  "songs": [
    {{
      "time": "時間",
      "title": "曲名",
      "artist": "アーティスト名（不明なら空文字）"
    }}
  ]
}}

# ルール
- sectionsは話題の切れ目で区切る（5〜10分ごと目安）
- songsはMCが「〜の〜です」「〜をかけます」など曲紹介している箇所を探す
- 曲が見当たらない場合はsongsは空配列でOK
- JSONのみ返す

# 文字起こし
{text}
"""

    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )

    text_response = message.content[0].text.strip()
    if text_response.startswith("```"):
        text_response = text_response.split("```")[1]
        if text_response.startswith("json"):
            text_response = text_response[4:]

    return json.loads(text_response)

def summarize_full(all_sections, all_songs, segments):
    """全体のあらすじとトピックをまとめて生成"""
    sections_text = "\n".join([
        f"{s['time_range']} {s['title']}：{s['description']}"
        for s in all_sections
    ])

    prompt = f"""
以下はラジオ番組の各セクションの要約です。
全体のまとめを作ってください。

# 出力形式（JSON）
{{
  "topics": ["話題1", "話題2", ...],
  "summary": "放送全体のあらすじを400〜500文字で"
}}

# セクション一覧
{sections_text}

JSONのみ返してください。
"""

    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    text_response = message.content[0].text.strip()
    if text_response.startswith("```"):
        text_response = text_response.split("```")[1]
        if text_response.startswith("json"):
            text_response = text_response[4:]

    return json.loads(text_response)

def main():
    video_id = "-EiQyBZaBLk"

    with open(f"data/{video_id}_raw.json", "r", encoding="utf-8") as f:
        raw = json.load(f)

    segments = raw["segments"]

    # 60分（3600秒）ごとに分割
    chunk_size = 3600
    max_time = segments[-1]["start"]
    chunks = []
    for start in range(0, int(max_time) + 1, chunk_size):
        chunk = [s for s in segments if start <= s["start"] < start + chunk_size]
        if chunk:
            chunks.append(chunk)

    print(f"全{len(chunks)}チャンクに分割して処理します...")

    all_sections = []
    all_songs = []

    for i, chunk in enumerate(chunks):
        start_min = int(chunk[0]["start"] // 60)
        print(f"チャンク {i+1}/{len(chunks)}（{start_min}分〜）を処理中...")
        result = summarize_chunk(chunk)
        all_sections.extend(result.get("sections", []))
        all_songs.extend(result.get("songs", []))

    print("全体まとめを生成中...")
    full_summary = summarize_full(all_sections, all_songs, segments)

    final = {
        "sections": all_sections,
        "songs": all_songs,
        "topics": full_summary["topics"],
        "summary": full_summary["summary"]
    }

    with open(f"data/{video_id}_summary.json", "w", encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False, indent=2)

    print(f"\n=== 完了 ===")
    print(f"セクション数: {len(all_sections)}")
    print(f"曲数: {len(all_songs)}")
    print(f"トピック: {final['topics']}")
    print(f"あらすじ: {final['summary'][:100]}...")

if __name__ == "__main__":
    main()