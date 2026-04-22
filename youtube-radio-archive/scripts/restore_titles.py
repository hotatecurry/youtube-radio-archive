import json, re, time
from pathlib import Path
from urllib.request import urlopen, Request

SCRIPTS_DIR = Path(__file__).parent
OUT_DIR = SCRIPTS_DIR / "../src/data"

videos_path = OUT_DIR / "videos.json"
with open(videos_path, "r", encoding="utf-8") as f:
    videos = json.load(f)

# タイトルがIDのままのものだけ対象
missing = [v for v in videos if v["title"] == v["id"]]
print(f"タイトル欠損: {len(missing)}本")

for i, v in enumerate(missing):
    vid = v["id"]
    try:
        url = f"https://www.youtube.com/watch?v={vid}"
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        html = urlopen(req).read().decode()
        m = re.search(r'<title>(.+?) - YouTube</title>', html)
        title = m.group(1) if m else vid
        v["title"] = title
        print(f"  [{i+1}/{len(missing)}] {vid} → {title}")
    except Exception as e:
        print(f"  ❌ {vid}: {e}")
    time.sleep(1)

with open(videos_path, "w", encoding="utf-8") as f:
    json.dump(videos, f, ensure_ascii=False, indent=2)
print(f"\n✅ 復元完了")