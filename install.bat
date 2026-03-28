@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo  ============================================================
echo    Mewgenics 日本語MOD インストーラー (v2.0)
echo  ============================================================
echo.

:: -----------------------------------------------------------
:: Steam ゲームフォルダの自動検出
:: -----------------------------------------------------------
set "GAME_DIR="

:: レジストリから Steam パスを取得
for /f "tokens=2*" %%a in ('reg query "HKLM\SOFTWARE\Valve\Steam" /v InstallPath 2^>nul') do set "STEAM_PATH=%%b"
if not defined STEAM_PATH (
    for /f "tokens=2*" %%a in ('reg query "HKLM\SOFTWARE\WOW6432Node\Valve\Steam" /v InstallPath 2^>nul') do set "STEAM_PATH=%%b"
)

if defined STEAM_PATH (
    :: メインライブラリを確認
    if exist "!STEAM_PATH!\steamapps\common\Mewgenics\Mewgenics.exe" (
        set "GAME_DIR=!STEAM_PATH!\steamapps\common\Mewgenics"
        goto :found
    )

    :: libraryfolders.vdf から追加ライブラリを検索
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

:: よくあるパスをフォールバック検索
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

:: 見つからなかった場合、手動入力
echo  Mewgenics のゲームフォルダが見つかりませんでした。
echo.
echo  確認方法:
echo    Steam → Mewgenics → 右クリック → 管理
echo    → ローカルファイルを閲覧
echo.
set /p "GAME_DIR=  ゲームフォルダのパス: "
set "GAME_DIR=!GAME_DIR:"=!"

if not exist "!GAME_DIR!\Mewgenics.exe" (
    echo.
    echo  エラー: Mewgenics.exe が見つかりません。
    echo  正しいゲームフォルダを指定してください。
    echo.
    pause
    exit /b 1
)

:found
echo  ゲームフォルダ: !GAME_DIR!
echo.

:: -----------------------------------------------------------
:: 既存MODのチェック
:: -----------------------------------------------------------
:: 旧方式 (v1.x) の残骸があれば整合性確認を案内
if exist "!GAME_DIR!\Mewgenics.exe.backup" goto :old_mod
if exist "!GAME_DIR!\resources.gpak.backup" goto :old_mod
if exist "!GAME_DIR!\mewgenics_jp_state.json" goto :old_mod
goto :no_old_mod

:old_mod
echo  旧バージョン (v1.x) の日本語MODが検出されました。
echo.
echo  先に Steam でファイルの整合性を確認してください。
echo    Steam → Mewgenics → 右クリック → プロパティ
echo    → インストール済みファイル → ファイルの整合性を確認
echo.
set /p "CONFIRM=  整合性確認は済みましたか？ (Y/N): "
if /i not "!CONFIRM!"=="Y" (
    echo.
    echo  整合性確認を行ってから再度実行してください。
    pause
    exit /b 0
)
echo.

:no_old_mod
if exist "!GAME_DIR!\version.dll" (
    echo  既存の日本語MODを更新します。
    echo.
)

:: -----------------------------------------------------------
:: ファイルコピー
:: -----------------------------------------------------------
echo.
echo  インストール中...

:: version.dll をコピー
copy /y "version.dll" "!GAME_DIR!\version.dll" >nul
if errorlevel 1 (
    echo  エラー: version.dll のコピーに失敗しました。
    echo  ゲームが起動中の場合は終了してから再試行してください。
    pause
    exit /b 1
)

:: MewgenicsJP フォルダをコピー
xcopy /e /i /y "MewgenicsJP" "!GAME_DIR!\MewgenicsJP" >nul
if errorlevel 1 (
    echo  エラー: MewgenicsJP フォルダのコピーに失敗しました。
    pause
    exit /b 1
)

:: 古いバックアップとキャッシュを削除 (再ビルドを強制)
if exist "!GAME_DIR!\resources.gpak.bak" del "!GAME_DIR!\resources.gpak.bak"
if exist "!GAME_DIR!\MewgenicsJP\.gpak_state" del "!GAME_DIR!\MewgenicsJP\.gpak_state"

:: 旧方式の残骸を削除
if exist "!GAME_DIR!\resources.gpak.backup" del "!GAME_DIR!\resources.gpak.backup"
if exist "!GAME_DIR!\Mewgenics.exe.backup" del "!GAME_DIR!\Mewgenics.exe.backup"
if exist "!GAME_DIR!\mewgenics_jp_state.json" del "!GAME_DIR!\mewgenics_jp_state.json"

:: 言語設定を ja に変更
set "SETTINGS_DIR=%APPDATA%\Glaiel Games\Mewgenics"
if exist "!SETTINGS_DIR!" (
    for /d %%d in ("!SETTINGS_DIR!\*") do (
        set "SETTINGS_FILE=%%d\settings.txt"
        if exist "!SETTINGS_FILE!" (
            powershell -NoProfile -Command "(Get-Content '!SETTINGS_FILE!') -replace 'current_language \w+','current_language ja' | Set-Content '!SETTINGS_FILE!'" >nul 2>&1
        )
    )
)

echo.
echo  ============================================================
echo    インストール完了！
echo  ============================================================
echo.
echo  ゲームを起動すると日本語化されます。
echo.

pause
exit /b 0
