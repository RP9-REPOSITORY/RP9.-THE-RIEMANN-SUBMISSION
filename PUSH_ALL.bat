@echo off
setlocal EnableExtensions DisableDelayedExpansion
title RP9 - PUSH ALL
set "REPO_DIR=F:\GitHub\RP9.-THE-RIEMANN-SUBMISSION"

echo ==============================================
echo RP9 - PUSH ALL
echo ==============================================
echo.
if not exist "%REPO_DIR%\" (
    echo ERROR: Repository directory not found:
    echo "%REPO_DIR%"
    goto FINISH
)
cd /d "%REPO_DIR%"
if errorlevel 1 (
    echo ERROR: Cannot enter repository directory.
    goto FINISH
)
where git >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git executable not found.
    goto FINISH
)
git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not initialized here.
    echo Initialize and connect the repository using CMD first.
    goto FINISH
)
echo Repository: %CD%
echo.
git status
if errorlevel 1 goto FAILED
echo.
choice /C YN /N /M "Stage ALL changes, including deletions? [Y/N]: "
if errorlevel 2 goto FINISH

git add -A
if errorlevel 1 goto FAILED

git diff --cached --quiet
if errorlevel 2 goto FAILED
if not errorlevel 1 goto PUSH

echo.
set "COMMIT_MSG=Update RP9 repository"
set /p "COMMIT_MSG=Commit message [Update RP9 repository]: "
if not defined COMMIT_MSG set "COMMIT_MSG=Update RP9 repository"
git commit -m "%COMMIT_MSG%"
if errorlevel 1 goto FAILED

:PUSH
echo.
echo Pushing current branch to origin...
git push -u origin HEAD
if errorlevel 1 goto FAILED
echo.
echo SUCCESS: Push completed.
goto FINISH

:FAILED
echo.
echo ERROR: A Git command failed. See the output above.

:FINISH
echo.
echo ==============================================
echo PUSH ALL - FINISHED
echo ==============================================
pause
endlocal
exit /b
