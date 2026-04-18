import json
from pathlib import Path

base = Path(r"C:\Users\manab\pikuhami\youtube-radio-archive")
videos_path = base / "src" / "data" / "videos.json"
summary_dir = base / "scripts" / "data"
backup_path = base / "src" / "data" / "videos.json.bak"

with open(videos_path, encoding="utf-8") as f:
    videos = json.load(f)

summary_map = {}
for p in summary_dir.glob("*_summary.json"):
    vid = p.stem.replace("_summary", "")
    with open(p, encoding="utf-8") as f:
        summary_map[vid] = json.load(f)

updated = 0
for v in videos:
    sid = v.get("id")
    if sid in summary_map:
        v["summary"] = summary_map[sid]
        v["has_summary"] = True
        updated += 1

backup_path.write_text(videos_path.read_text(encoding="utf-8"), encoding="utf-8")
with open(videos_path, "w", encoding="utf-8") as f:
    json.dump(videos, f, ensure_ascii=False, indent=2)

print(f"updated={updated}")
print(f"saved={videos_path}")