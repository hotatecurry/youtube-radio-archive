from youtube_transcript_api import YouTubeTranscriptApi
from urllib.request import urlopen
import json
import os
import re

def get_transcript_with_timestamps(video_id):
    try:
        ytt = YouTubeTranscriptApi()
        transcript = ytt.fetch(video_id, languages=['ja'])
        # タイムスタンプ付きで保存
        segments = [{"start": t.start, "text": t.text} for t in transcript]
        return segments
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_chapters(video_id):
    """YouTubeの動画説明文からチャプター情報を取得"""
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        html = urlopen(url).read().decode()
        
        # 説明文からチャプターっぽいパターンを抽出
        pattern = r'(\d{1,2}:\d{2}(?::\d{2})?)\s+(.+?)(?=\n\d{1,2}:\d{2}|$)'
        chapters = re.findall(pattern, html[:5000])
        return [{"time": c[0], "title": c[1].strip()} for c in chapters]
    except Exception as e:
        print(f"チャプター取得エラー: {e}")
        return []

def main():
    video_id = "-EiQyBZaBLk"
    
    print(f"字幕取得中: {video_id}")
    segments = get_transcript_with_timestamps(video_id)
    
    if segments:
        print(f"取得成功！セグメント数: {len(segments)}")
        
        chapters = get_chapters(video_id)
        print(f"チャプター数: {len(chapters)}")
        
        os.makedirs("data", exist_ok=True)
        data = {
            "video_id": video_id,
            "segments": segments,
            "chapters": chapters
        }
        with open(f"data/{video_id}_raw.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"data/{video_id}_raw.json に保存しました")

if __name__ == "__main__":
    main()