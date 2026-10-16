@echo off
setlocal EnableExtensions DisableDelayedExpansion
title RP9 - Push and GitHub Pages
cd /d "F:\GitHub\RP9.-THE-RIEMANN-SUBMISSION"
if errorlevel 1 goto failed
where git >nul 2>&1
if errorlevel 1 goto failed
git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 goto failed
set "BRANCH="
for /f "delims=" %%B in ('git branch --show-current') do set "BRANCH=%%B"
if not "%BRANCH%"=="main" (
    echo ERROR: Expected branch main. No changes were made.
    goto failed
)
echo Repository: F:\GitHub\RP9.-THE-RIEMANN-SUBMISSION
echo.
git remote -v
echo.
git status --short
echo.
echo Staging all changes, including deletions...
git add -A
if errorlevel 1 goto failed
git diff --cached --quiet
if errorlevel 2 goto failed
if errorlevel 1 goto commit_changes
echo No file changes. Creating a deployment trigger commit...
git commit --allow-empty -m "Trigger RP9 Pages deployment"
if errorlevel 1 goto failed
goto push
:commit_changes
git commit -m "Update RP9 repository and website"
if errorlevel 1 goto failed
:push
git push -u origin main
if errorlevel 1 goto failed
echo.
echo PUSH COMPLETED.
echo GitHub Pages publishes only if a Pages workflow runs on push to main.
echo The website is ready when its deployment succeeds in GitHub Actions.
set "REPO_URL="
for /f "delims=" %%U in ('git remote get-url origin') do set "REPO_URL=%%U"
set "REPO_URL=%REPO_URL:git@github.com:=https://github.com/%"
set "REPO_URL=%REPO_URL:.git=%"
if defined REPO_URL start "" "%REPO_URL%/actions"
echo.
pause
exit /b 0
:failed
echo.
echo ERROR: Operation stopped. Read the error above.
echo No force push or automatic merge was performed.
pause
exit /b 1
