# filter_videos.py
from googleapiclient.discovery import build

API_KEY = "AIzaSyBe8s4VTpP-WmN2g2eFK1HBoUvkRwhiK-A"
KEYWORD = "ピクルスはみ出てますよ"  # 例："ハンバーガー対談"

youtube = build("youtube", "v3", developerKey=API_KEY)

with open("video_ids.txt") as f:
    all_ids = [line.strip() for line in f if line.strip()]

# 50本ずつバッチでタイトル取得（APIクォータ節約）
filtered = []
for i in range(0, len(all_ids), 50):
    batch = all_ids[i:i+50]
    resp = youtube.videos().list(
        part="snippet",
        id=",".join(batch)
    ).execute()
    for item in resp["items"]:
        title = item["snippet"]["title"]
        if KEYWORD in title:
            filtered.append(item["id"])
            print(f"✅ {title}")

with open("filtered_ids.txt", "w") as f:
    for vid in filtered:
        f.write(vid + "\n")

print(f"\n絞り込み完了: {len(filtered)}本 → filtered_ids.txt に保存")