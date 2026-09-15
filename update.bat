@echo off
chcp 65001 >nul
cd /d "%~dp0"
python scan.py || goto :fail
git add -A
git diff --cached --quiet && (echo 没有新变化。 & goto :end)
git commit -m "Update %date% %time:~0,5%" || goto :fail
git push || goto :fail
echo.
echo 已推送，网页约 1 分钟后更新。
goto :end
:fail
echo 出错了，请检查上面的信息。
:end
pause
