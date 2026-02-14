@echo off
chcp 65001 >nul 2>&1
title Mewgenics 日本語MOD アンインストーラー

cd /d "%~dp0"

if not exist "python\python.exe" (
    echo.
    echo  エラー: python\python.exe が見つかりません。
    echo  ZIP ファイルが正しく展開されていることを確認してください。
    echo.
    pause
    exit /b 1
)

python\python.exe -m patcher.uninstall_mod

exit /b %ERRORLEVEL%
