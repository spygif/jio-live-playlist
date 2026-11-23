@echo off
title Sync Jio Live Playlist to GitHub
cd /d "%~dp0"
echo ============================================================
echo   Jio STB Auto-Updating Live Playlist - GitHub Sync
echo ============================================================
echo.

git remote get-url origin >nul 2>&1
if %errorlevel% equ 0 (
    echo [*] Remote origin is already configured.
    echo [*] Pushing latest changes to GitHub...
    git add -A
    git commit -m "Update workflow" >nul 2>&1
    git push -u origin main
    goto finished
)

echo 1. Go to https://github.com/new and create a new repository:
echo    - Repository name: jio-live-playlist (or any name you prefer)
echo    - Choose: Public (or Private)
echo    - Do NOT check "Add a README file"
echo    - Click "Create repository"
echo.
set /p REPO_URL="Paste your GitHub repository HTTPS URL here: "

if "%REPO_URL%"=="" (
    echo [ERROR] No repository URL provided. Exiting.
    pause
    exit /b 1
)

echo.
echo [*] Initializing git repository...
git init
git branch -M main
git add .
git commit -m "Initial commit: Jio STB Auto-Updating Playlist & Workflow"
git remote remove origin >nul 2>&1
git remote add origin %REPO_URL%

echo [*] Pushing files to GitHub...
git push -u origin main

:finished
if %errorlevel% neq 0 (
    echo.
    echo [!] Push encountered an issue. Please verify you are logged in to GitHub.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo [SUCCESS] Your repository is synchronized with GitHub!
echo ============================================================
echo.
echo [*] IMPORTANT STEP: Enable GitHub Actions Workflow Permissions:
echo     1. Open your repository on GitHub in your browser.
echo     2. Go to: Settings -> Actions -> General.
echo     3. Scroll to "Workflow permissions".
echo     4. Select "Read and write permissions" and click Save.
echo.
echo [*] Your Master Playlist Raw URL for OwnTV:
echo     https://raw.githubusercontent.com/spygif/jio-live-playlist/main/playlist.m3u
echo.
pause
