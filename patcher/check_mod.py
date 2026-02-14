"""
MOD 整合性チェック (Steam ラウンチオプション用)

ゲーム起動前に MOD が適用されているか確認し、
Steam アップデートで上書きされていた場合は言語を en に戻して警告する。

Steam ラウンチオプション設定:
  "C:\...\MewgenicsJP\python\python.exe" -m patcher.check_mod %command%
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

with open(SCRIPT_DIR / "config.json", "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

SETTINGS_DIR_NAME = "Glaiel Games/Mewgenics"
SETTINGS_FILE_NAME = "settings.txt"
ZWSP_SIGNATURE = bytes.fromhex(CONFIG["patch_signatures"]["zwsp_cmp_r9w"])


def find_game_dir_from_args():
    """%command% からゲームの exe パスを取得"""
    for arg in sys.argv[1:]:
        p = Path(arg)
        if p.name.lower() == "mewgenics.exe" and p.exists():
            return p.parent
    return None


def find_game_dir_from_state():
    """state ファイルからゲームフォルダを探す"""
    from . import steam_finder
    return steam_finder.find_game_path()


def is_mod_applied(game_dir):
    """MOD が適用されているか確認 (exe に ZWSP パッチがあるか)"""
    exe = game_dir / CONFIG["exe_name"]
    if not exe.exists():
        return False
    with open(exe, "rb") as f:
        data = f.read()
    return ZWSP_SIGNATURE in data


def reset_language_en():
    """言語設定を en に戻す"""
    appdata = os.environ.get("APPDATA", "")
    if not appdata:
        return False

    settings_root = Path(appdata) / SETTINGS_DIR_NAME
    if not settings_root.exists():
        return False

    reset = False
    for settings_file in settings_root.rglob(SETTINGS_FILE_NAME):
        try:
            text = settings_file.read_text(encoding="utf-8")
        except OSError:
            continue
        if "current_language ja" in text:
            new_text = re.sub(r"current_language \w+", "current_language en", text)
            settings_file.write_text(new_text, encoding="utf-8")
            reset = True

    return reset


def main():
    # %command% からゲーム exe を探す
    game_dir = find_game_dir_from_args()
    if not game_dir:
        game_dir = find_game_dir_from_state()

    if game_dir and not is_mod_applied(game_dir):
        # MOD が消えている → Steam アップデートで上書きされた
        reset_language_en()

        # 警告メッセージ (MessageBox)
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(
                0,
                "Steam のアップデートにより日本語MOD が無効になりました。\n\n"
                "言語設定を English に戻しました。\n"
                "ゲームは英語で起動します。\n\n"
                "日本語に戻すには install.bat を再度実行してください。",
                "Mewgenics 日本語MOD",
                0x30  # MB_ICONWARNING
            )
        except Exception:
            pass

    # ゲームを起動 (%command% の引数をそのまま実行)
    game_args = sys.argv[1:]
    if game_args:
        subprocess.Popen(game_args)


if __name__ == "__main__":
    main()
