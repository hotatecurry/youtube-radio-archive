@echo off
chcp 65001 > nul
cd /d C:\Users\manab\pikuhami

echo リモートの最新状態を取得中...
git pull origin main

echo skipファイルを削除中（excluded除く）...
python scripts\cleanup_skip.py

echo 動画情報・要約を更新中...
python scripts\update.py

echo Gitにコミット＆プッシュ中...
git add -A
git commit -m "Add summary: manual update"
git push origin main

echo 完了！
pause