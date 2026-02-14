"""
Mewgenics 日本語MOD アンインストーラー

バックアップからゲームファイルを復元する。
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def _setup_console():
    """Windows コンソールを UTF-8 に設定"""
    if sys.platform == "win32":
        subprocess.run(["chcp", "65001"], shell=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        os.system("title Mewgenics JP MOD Uninstaller")

SCRIPT_DIR = Path(__file__).parent

with open(SCRIPT_DIR / "config.json", "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

EXE_NAME = CONFIG["exe_name"]
GPAK_NAME = CONFIG["gpak_name"]
BACKUP_SUFFIX = CONFIG["backup_suffix"]
STATE_FILE = CONFIG["state_file"]


SETTINGS_DIR_NAME = "Glaiel Games/Mewgenics"
SETTINGS_FILE_NAME = "settings.txt"


def print_header():
    print()
    print("=" * 56)
    print("  Mewgenics 日本語MOD アンインストーラー")
    print("=" * 56)
    print()


def reset_language_setting():
    """ゲームの言語設定を en に戻す。

    Returns:
        True: 自動リセット成功 or 元から en
        False: settings.txt が見つからない (手動対応が必要)
    """
    # %APPDATA%/Glaiel Games/Mewgenics/<steam_id>/settings.txt
    appdata = os.environ.get("APPDATA", "")
    if not appdata:
        return False

    settings_root = Path(appdata) / SETTINGS_DIR_NAME
    if not settings_root.exists():
        return False

    found = False
    for settings_file in settings_root.rglob(SETTINGS_FILE_NAME):
        try:
            text = settings_file.read_text(encoding="utf-8")
        except OSError:
            continue

        if "current_language ja" not in text:
            print(f"  言語設定: 既に en です ({settings_file.parent.name})")
            found = True
            continue

        new_text = text.replace("current_language ja", "current_language en")
        settings_file.write_text(new_text, encoding="utf-8")
        print(f"  言語設定: ja → en にリセットしました ({settings_file.parent.name})")
        found = True

    return found


def do_uninstall():
    """アンインストール処理"""
    print_header()

    # ゲームフォルダ検出
    print("[1/4] Steam ゲームフォルダを検出中...")
    from . import steam_finder
    game_dir = steam_finder.detect_game_dir()
    if not game_dir:
        print("\n  エラー: ゲームフォルダが見つかりません。")
        return False

    print(f"  検出: {game_dir}")

    gpak = game_dir / GPAK_NAME
    gpak_bak = game_dir / (GPAK_NAME + BACKUP_SUFFIX)
    exe = game_dir / EXE_NAME
    exe_bak = game_dir / (EXE_NAME + BACKUP_SUFFIX)
    state_path = game_dir / STATE_FILE

    # バックアップ存在確認
    if not gpak_bak.exists() and not exe_bak.exists():
        print("\n  バックアップが見つかりません。")
        print("  MODがインストールされていないか、")
        print("  Steamの「ゲームファイルの整合性を確認」を使用してください。")
        return False

    # ゲーム実行中チェック
    print("\n[2/4] ゲーム実行状態を確認中...")
    try:
        f = open(exe, "r+b")
        f.close()
    except (PermissionError, OSError):
        print("  エラー: ゲームが実行中です。")
        print("  ゲームを終了してから再度実行してください。")
        return False
    print("  OK")

    # 言語設定リセット
    print("\n[3/4] 言語設定をリセット中...")
    if not reset_language_setting():
        print("  警告: 言語設定ファイルが見つかりませんでした。")
        print("  アンインストール後にゲームが起動できない場合は、")
        print("  install.bat で再インストールしてから")
        print("  ゲーム内で Settings → Language → English に")
        print("  変更した後、再度アンインストールしてください。")
        print()
        ans = input("  続行しますか? (Y/n): ").strip().lower()
        if ans == "n":
            return False

    # 復元
    print("\n[4/4] ゲームファイルを復元中...")
    restored = 0

    if gpak_bak.exists():
        print(f"  {GPAK_NAME} を復元中...")
        shutil.copy2(gpak_bak, gpak)
        gpak_bak.unlink()
        print(f"    完了 ({gpak.stat().st_size / (1024**3):.2f} GB)")
        restored += 1
    else:
        print(f"  {GPAK_NAME}: バックアップなし (スキップ)")

    if exe_bak.exists():
        print(f"  {EXE_NAME} を復元中...")
        shutil.copy2(exe_bak, exe)
        exe_bak.unlink()
        print(f"    完了 ({exe.stat().st_size / (1024**2):.1f} MB)")
        restored += 1
    else:
        print(f"  {EXE_NAME}: バックアップなし (スキップ)")

    # 状態ファイル削除
    if state_path.exists():
        state_path.unlink()

    if restored > 0:
        print()
        print("=" * 56)
        print("  アンインストール完了!")
        print("=" * 56)
        print()
        print("  ゲームファイルを元の状態に復元しました。")
        print("  バックアップファイルは削除されました。")
        print()
    else:
        print("\n  復元するファイルがありませんでした。")

    return True


def main():
    _setup_console()
    try:
        success = do_uninstall()
    except KeyboardInterrupt:
        print("\n\n  中断されました。")
        success = False
    except Exception as e:
        print(f"\n  予期しないエラー: {e}")
        success = False

    if not success:
        print()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
