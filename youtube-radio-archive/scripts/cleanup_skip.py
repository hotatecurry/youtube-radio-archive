from pathlib import Path

scripts_dir = Path(__file__).parent
excluded_file = scripts_dir / "excluded_ids.txt"
excluded_ids = set()
if excluded_file.exists():
    with open(excluded_file, "r", encoding="utf-8") as f:
        excluded_ids = {line.strip() for line in f if line.strip()}

deleted = []
for skip_file in (scripts_dir / "data").glob("*_skip.json"):
    vid = skip_file.stem.replace("_skip", "")
    if vid not in excluded_ids:
        skip_file.unlink()
        deleted.append(vid)

print(f"削除: {deleted}")
print(f"保持: {excluded_ids}")