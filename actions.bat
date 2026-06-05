@echo off
setlocal enabledelayedexpansion

REM Activate Python venv
call .venv\Scripts\activate

REM Default: show usage if wrong/no args
if "%1"=="" (
    echo Usage:
    echo   actions update [patch^|minor^|major] [--release]
    echo   actions rollback-version
    echo.
    echo Examples:
    echo   actions update patch --release        ^(bump patch + push + release to PyPI^)
    echo   actions update minor                  ^(bump minor + push only^)
    echo   actions rollback-version              ^(undo version bump only, preserve code changes^)
    exit /b 1
)

REM Rollback version-only command (undo bump without losing code changes)
if "%1"=="rollback-version" (
    call :rollback_version_only
    exit /b %ERRORLEVEL%
)

REM Version bump & build logic
if "%2"=="patch" (
    call :verify_version_bump patch
    if !ERRORLEVEL! neq 0 exit /b 1
    
    bumpver update --patch --allow-dirty
    git add -u
    python devops-scripts\generate_commit.py
    del /q dist\* 2>nul
    python -m build
    call :confirm_push || ( call :rollback & goto :eof )
    git push --follow-tags
    if "%3"=="--release" (
        for /f %%V in ('bumpver show --current-version --no-fetch') do set VERSION=%%V
        gh release create v!VERSION! --title "v!VERSION!" --notes "Automated release"
        set /p PYPI_TOKEN=<keys\pypi.txt
        twine upload dist/* -u __token__ -p !PYPI_TOKEN!
    )
    goto :eof
)
if "%2"=="minor" (
    call :verify_version_bump minor
    if !ERRORLEVEL! neq 0 exit /b 1
    
    bumpver update --minor --allow-dirty
    git add -u
    python devops-scripts\generate_commit.py
    del /q dist\* 2>nul
    python -m build
    call :confirm_push || ( call :rollback & goto :eof )
    git push --follow-tags
    if "%3"=="--release" (
        for /f %%V in ('bumpver show --current-version --no-fetch') do set VERSION=%%V
        gh release create v!VERSION! --title "v!VERSION!" --notes "Automated release"
        set /p PYPI_TOKEN=<keys\pypi.txt
        twine upload dist/* -u __token__ -p !PYPI_TOKEN!
    )
    goto :eof
)
if "%2"=="major" (
    call :verify_version_bump major
    if !ERRORLEVEL! neq 0 exit /b 1
    
    bumpver update --major --allow-dirty
    git add -u
    python devops-scripts\generate_commit.py
    del /q dist\* 2>nul
    python -m build
    call :confirm_push || ( call :rollback & goto :eof )
    git push --follow-tags
    if "%3"=="--release" (
        for /f %%V in ('bumpver show --current-version --no-fetch') do set VERSION=%%V
        gh release create v!VERSION! --title "v!VERSION!" --notes "Automated release"
        set /p PYPI_TOKEN=<keys\pypi.txt
        twine upload dist/* -u __token__ -p !PYPI_TOKEN!
    )
    goto :eof
)

echo Usage: actions update [patch^|minor^|major] [--release]
exit /b 1


REM ── Roll back bump and unstage everything ───────────────────────────────────
git restore --staged .
git restore .
echo  Done. Changes have been rolled back to pre-bump state.
exit /b 0

:rollback
echo  Rolling back version bump...
for /f %%V in ('git describe --tags --abbrev=0') do set VERSION=%%V
git tag -d %VERSION% 2>nul
git reset --hard HEAD~1
echo  Done. Changes have been rolled back to pre-bump state.
exit /b 0


REM ── Confirmation prompt ─────────────────────────────────────────────────────
:confirm_push
echo.
echo  Ready to push. Press ENTER to confirm or ESC to abort...
call :read_key
if "%KEYPRESS%"=="ENTER" (
    echo  Pushing...
    exit /b 0
)
echo  Aborted.
exit /b 1

:read_key
set "KEYPRESS="
for /f "delims=" %%k in ('powershell -noprofile -command "$k = $host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown'); if ($k.VirtualKeyCode -eq 13) { \"ENTER\" } elseif ($k.VirtualKeyCode -eq 27) { \"ESC\" } else { \"OTHER\" }"') do set "KEYPRESS=%%k"
exit /b 0


REM ── Version verification (prevent skipping versions) ────────────────────────
:verify_version_bump
setlocal enabledelayedexpansion
set BUMP_TYPE=%1

REM Get current local version
for /f %%V in ('bumpver show --current-version --no-fetch') do set CURRENT_VERSION=%%V

REM Simulate the bump to see what version will be created
for /f %%V in ('bumpver show --new-version --no-fetch --%BUMP_TYPE%') do set NEW_VERSION=%%V

REM Try to get GitHub version (latest tag on origin)
for /f %%V in ('git describe --tags --abbrev=0 origin/main 2^>nul') do set GITHUB_VERSION=%%V

if "!GITHUB_VERSION!"=="" (
    echo Warning: Could not fetch version from GitHub ^(might be offline or no tags yet^)
    exit /b 0
)

REM Remove 'v' prefix if present for comparison
set GITHUB_VER=!GITHUB_VERSION:v=!
set NEW_VER=!NEW_VERSION:v=!

REM Simple check: verify new version is different from current and is sensible
if "!NEW_VER!"=="!CURRENT_VERSION!" (
    echo Error: New version !NEW_VER! is same as current !CURRENT_VERSION!
    exit /b 1
)

echo.
echo Version verification:
echo   Current local:   !CURRENT_VERSION!
echo   Latest GitHub:   !GITHUB_VER!
echo   Will bump to:    !NEW_VER!
echo.

REM Warn if local version is ahead of GitHub (likely a previous un-pushed bump)
if "!CURRENT_VERSION!" neq "!GITHUB_VER!" (
    echo Warning: Local version !CURRENT_VERSION! differs from GitHub !GITHUB_VER!
    echo This might mean you have a previous unbumped commit locally.
    echo.
    set /p CONFIRM="Continue anyway? (y/n): "
    if /i not "!CONFIRM!"=="y" (
        echo Aborted.
        exit /b 1
    )
)

exit /b 0


REM ── Rollback version changes only (preserves code changes) ──────────────────
:rollback_version_only
echo.
echo Rolling back version to previous commit...
echo.

REM Get previous version from last commit
for /f %%V in ('git show HEAD~1:bumpver.toml 2^>nul ^| findstr "current_version"') do set PREV_LINE=%%V
if "!PREV_LINE!"=="" (
    echo Error: Could not find previous version in git history.
    exit /b 1
)

REM Parse version from line like: current_version = "1.2.3"
for /f "tokens=3 delims== " %%V in ("!PREV_LINE!") do set PREV_VERSION=%%V
set PREV_VERSION=!PREV_VERSION:"=!

echo Previous version detected: !PREV_VERSION!

REM Restore only version-related files from previous commit
echo Restoring version files...
git checkout HEAD~1 -- bumpver.toml
git checkout HEAD~1 -- pyproject.toml
git checkout HEAD~1 -- leetcrate/__init__.py
git checkout HEAD~1 -- leetcrate/generators/__init__.py

REM Stage the restored files
git add bumpver.toml pyproject.toml leetcrate/__init__.py leetcrate/generators/__init__.py

REM Create a new commit undoing the version bump
git commit -m "chore: revert version bump to !PREV_VERSION!"

REM Delete the tag created by the bump
for /f %%V in ('git describe --tags --abbrev=0') do set TAG_TO_DELETE=%%V
git tag -d !TAG_TO_DELETE! 2>nul

echo.
echo Done. Version rolled back to !PREV_VERSION!
echo ^(Code changes preserved in new commit^)
exit /b 0