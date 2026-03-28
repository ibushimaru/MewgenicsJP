@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo  ============================================================
echo    Mewgenics 日本語MOD アンインストーラー
echo  ============================================================
echo.

:: -----------------------------------------------------------
:: Steam ゲームフォルダの自動検出
:: -----------------------------------------------------------
set "GAME_DIR="

for /f "tokens=2*" %%a in ('reg query "HKLM\SOFTWARE\Valve\Steam" /v InstallPath 2^>nul') do set "STEAM_PATH=%%b"
if not defined STEAM_PATH (
    for /f "tokens=2*" %%a in ('reg query "HKLM\SOFTWARE\WOW6432Node\Valve\Steam" /v InstallPath 2^>nul') do set "STEAM_PATH=%%b"
)

if defined STEAM_PATH (
    if exist "!STEAM_PATH!\steamapps\common\Mewgenics\Mewgenics.exe" (
        set "GAME_DIR=!STEAM_PATH!\steamapps\common\Mewgenics"
        goto :found
    )

    set "VDF=!STEAM_PATH!\steamapps\libraryfolders.vdf"
    if exist "!VDF!" (
        for /f "tokens=1,2 delims=	 " %%a in ('findstr /c:"\"path\"" "!VDF!"') do (
            set "LIB_PATH=%%~b"
            set "LIB_PATH=!LIB_PATH:\\=\!"
            if exist "!LIB_PATH!\steamapps\common\Mewgenics\Mewgenics.exe" (
                set "GAME_DIR=!LIB_PATH!\steamapps\common\Mewgenics"
                goto :found
            )
        )
    )
)

for %%d in (C D E F G) do (
    if exist "%%d:\SteamLibrary\steamapps\common\Mewgenics\Mewgenics.exe" (
        set "GAME_DIR=%%d:\SteamLibrary\steamapps\common\Mewgenics"
        goto :found
    )
    if exist "%%d:\Steam\steamapps\common\Mewgenics\Mewgenics.exe" (
        set "GAME_DIR=%%d:\Steam\steamapps\common\Mewgenics"
        goto :found
    )
)

echo  Mewgenics のゲームフォルダが見つかりませんでした。
echo.
set /p "GAME_DIR=  ゲームフォルダのパス: "
set "GAME_DIR=!GAME_DIR:"=!"

if not exist "!GAME_DIR!\Mewgenics.exe" (
    echo.
    echo  エラー: Mewgenics.exe が見つかりません。
    pause
    exit /b 1
)

:found
echo  ゲームフォルダ: !GAME_DIR!
echo.

:: -----------------------------------------------------------
:: MODが存在するか確認
:: -----------------------------------------------------------
if not exist "!GAME_DIR!\version.dll" (
    if not exist "!GAME_DIR!\MewgenicsJP" (
        echo  日本語MODがインストールされていません。
        echo.
        pause
        exit /b 0
    )
)

:: -----------------------------------------------------------
:: アンインストール確認
:: -----------------------------------------------------------
set /p "CONFIRM=  日本語MODをアンインストールしますか？ (Y/N): "
if /i not "!CONFIRM!"=="Y" (
    echo.
    echo  キャンセルしました。
    pause
    exit /b 0
)

echo.
echo  アンインストール中...

:: version.dll を削除
if exist "!GAME_DIR!\version.dll" (
    del "!GAME_DIR!\version.dll"
    echo    version.dll を削除しました。
)

:: MewgenicsJP フォルダを削除
if exist "!GAME_DIR!\MewgenicsJP" (
    rmdir /s /q "!GAME_DIR!\MewgenicsJP"
    echo    MewgenicsJP フォルダを削除しました。
)

:: gpak バックアップがあれば復元
if exist "!GAME_DIR!\resources.gpak.bak" (
    del "!GAME_DIR!\resources.gpak"
    move "!GAME_DIR!\resources.gpak.bak" "!GAME_DIR!\resources.gpak" >nul
    echo    resources.gpak を復元しました。
)

:: 旧方式の残骸も削除
if exist "!GAME_DIR!\resources.gpak.backup" del "!GAME_DIR!\resources.gpak.backup"
if exist "!GAME_DIR!\Mewgenics.exe.backup" del "!GAME_DIR!\Mewgenics.exe.backup"
if exist "!GAME_DIR!\mewgenics_jp_state.json" del "!GAME_DIR!\mewgenics_jp_state.json"

:: 言語設定を en に戻す
set "SETTINGS_DIR=%APPDATA%\Glaiel Games\Mewgenics"
if exist "!SETTINGS_DIR!" (
    for /d %%d in ("!SETTINGS_DIR!\*") do (
        set "SETTINGS_FILE=%%d\settings.txt"
        if exist "!SETTINGS_FILE!" (
            powershell -NoProfile -Command "(Get-Content '!SETTINGS_FILE!') -replace 'current_language \w+','current_language en' | Set-Content '!SETTINGS_FILE!'" >nul 2>&1
        )
    )
)

echo.
echo  ============================================================
echo    アンインストール完了！
echo  ============================================================
echo.
echo  【推奨】 Steam でファイルの整合性を確認してください。
echo    Steam → Mewgenics → 右クリック → プロパティ
echo    → インストール済みファイル → ファイルの整合性を確認
echo.

pause
exit /b 0
