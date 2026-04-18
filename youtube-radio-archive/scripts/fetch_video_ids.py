from googleapiclient.discovery import build
import json

API_KEY = "AIzaSyBe8s4VTpP-WmN2g2eFK1HBoUvkRwhiK-A"   # ← Google Cloud ConsoleのAPIキーに置き換え
CHANNEL_ID = "UCzXARgBFSrU9stjHpHNmMBQ"  # ← 対象チャンネルIDに置き換え

def get_all_video_ids(api_key, channel_id):
    youtube = build("youtube", "v3", developerKey=api_key)
    
    # uploadsプレイリストIDを取得
    res = youtube.channels().list(part="contentDetails", id=channel_id).execute()
    uploads_id = res["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    
    # 全動画IDを取得（ページネーション対応）
    video_ids = []
    token = None
    while True:
        resp = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=uploads_id,
            maxResults=50,
            pageToken=token
        ).execute()
        for item in resp["items"]:
            video_ids.append(item["contentDetails"]["videoId"])
        token = resp.get("nextPageToken")
        if not token:
            break
    
    # video_ids.txtに保存
    with open("video_ids.txt", "w") as f:
        for vid in video_ids:
            f.write(vid + "\n")
    
    print(f"取得完了: {len(video_ids)}本 → video_ids.txt に保存")

get_all_video_ids(API_KEY, CHANNEL_ID)