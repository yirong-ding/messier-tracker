@echo off
chcp 65001 >nul
cd /d "%~dp0"
python scan.py || goto :fail
git add -A
git diff --cached --quiet && (echo Nothing new. & goto :end)
git commit -m "Update progress" || goto :fail
git push || goto :fail
echo.
echo Pushed. The site updates in about a minute.
goto :end
:fail
echo Something went wrong - see the messages above.
:end
pause
