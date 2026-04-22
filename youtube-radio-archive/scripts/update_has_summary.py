import json
import os

VIDEOS_JSON = r"C:\Users\manab\pikuhami\youtube-radio-archive\src\data\videos.json"
DATA_DIR    = r"C:\Users\manab\pikuhami\youtube-radio-archive\scripts\data"

with open(VIDEOS_JSON, encoding="utf-8") as f:
    videos = json.load(f)

updated = 0
for v in videos:
    has = os.path.exists(os.path.join(DATA_DIR, f"{v['id']}_summary.json"))
    if has and not v.get("has_summary"):
        v["has_summary"] = True
        updated += 1

with open(VIDEOS_JSON, "w", encoding="utf-8") as f:
    json.dump(videos, f, ensure_ascii=False, indent=2)

print(f"✅ {updated}本を has_summary=true に更新しました")