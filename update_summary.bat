@echo off
cd /d C:\Users\manab\pikuhami

echo 🔄 動画情報・要約を更新中...
python scripts/update.py

echo 📦 Gitにコミット＆プッシュ中...
git add -A
git commit -m "Add summary: manual update"
git push origin main

echo ✅ 完了！Cloudflare Pagesのデプロイをお待ちください。
pause