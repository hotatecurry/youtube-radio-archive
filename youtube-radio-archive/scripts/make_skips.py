import json
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
DATA_DIR = SCRIPTS_DIR / "data"
IDS_FILE = SCRIPTS_DIR / "filtered_ids.txt"

with open(IDS_FILE, "r", encoding="utf-8") as f:
    all_ids = [line.strip() for line in f if line.strip()]

count = 0
for vid in all_ids:
    summary = DATA_DIR / f"{vid}_summary.json"
    skip = DATA_DIR / f"{vid}_skip.json"
    if not summary.exists() and not skip.exists():
        with open(skip, "w", encoding="utf-8") as f:
            json.dump({"skipped": True, "reason": "no subtitles"}, f, ensure_ascii=False)
        print(f"  スキップ作成: {vid}")
        count += 1

print(f"\n✅ {count}本のスキップファイルを作成しました")