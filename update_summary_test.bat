@echo off
cd /d C:\Users\manab\pikuhami

echo --- 削除予定のskipファイル ---
for %%f in (scripts\data\*_skip.json) do (
    set "vid=%%~nf"
    setlocal enabledelayedexpansion
    set "vid=!vid:_skip=!"
    findstr /x /i "!vid!" scripts\excluded_ids.txt >nul 2>&1
    if errorlevel 1 echo %%f
    endlocal
)
echo --- ここまで ---
pause