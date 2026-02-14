"""
Mewgenics 日本語MOD アンインストーラー

2つのモード:
1. 言語設定のみリセット (ゲーム更新後の復旧用)
2. 完全アンインストール (ゲームファイルも復元)
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


def ask_mode():
    """ユーザーにモードを選択させる"""
    print("  操作を選択してください:")
    print()
    print("    1. 言語設定のみリセット")
    print("       (ゲーム更新後に起動できない場合はこちら)")
    print()
    print("    2. 完全アンインストール")
    print("       (ゲームファイルも元に戻します)")
    print()

    while True:
        ans = input("  番号を入力 (1/2): ").strip()
        if ans in ("1", "2"):
            return int(ans)
        print("  1 または 2 を入力してください。")


def do_language_reset():
    """言語設定のみリセット"""
    print()
    print("  言語設定をリセット中...")
    if reset_language_setting():
        print()
        print("=" * 56)
        print("  言語設定をリセットしました")
        print("=" * 56)
        print()
        print("  ゲームが英語で起動できるようになります。")
        print("  日本語に戻すには最新版の MOD をインストールしてください。")
        print()
    else:
        print("  言語設定ファイルが見つかりませんでした。")
        print("  手動で修正してください:")
        print('  Win+R →「%appdata%\\Glaiel Games\\Mewgenics」を開く')
        print("  数字フォルダの中の settings.txt を開き、")
        print('  「current_language ja」を「current_language en」に変更')
        print()

    return True


def do_full_uninstall(game_dir):
    """完全アンインストール (ゲームファイル復元 + 言語リセット)"""
    gpak = game_dir / GPAK_NAME
    gpak_bak = game_dir / (GPAK_NAME + BACKUP_SUFFIX)
    exe = game_dir / EXE_NAME
    exe_bak = game_dir / (EXE_NAME + BACKUP_SUFFIX)
    state_path = game_dir / STATE_FILE

    # ゲーム実行中チェック
    print("\n  ゲーム実行状態を確認中...")
    try:
        f = open(exe, "r+b")
        f.close()
    except (PermissionError, OSError):
        print("  エラー: ゲームが実行中です。")
        print("  ゲームを終了してから再度実行してください。")
        return False
    print("  OK")

    # 言語設定リセット
    print("\n  言語設定をリセット中...")
    if not reset_language_setting():
        print("  言語設定ファイルが見つかりませんでした。")

    # ゲームファイル復元
    print("\n  ゲームファイルを復元中...")

    if not gpak_bak.exists() and not exe_bak.exists():
        print("  バックアップが見つかりません。")
        print("  Steam から復元してください:")
        print("  Steam → Mewgenics → プロパティ")
        print("  → インストール済みファイル → ゲームファイルの整合性を確認")
        print()
        if state_path.exists():
            state_path.unlink()
        return True

    if gpak_bak.exists():
        print(f"  {GPAK_NAME} を復元中...")
        shutil.copy2(gpak_bak, gpak)
        gpak_bak.unlink()
        print(f"    完了 ({gpak.stat().st_size / (1024**3):.2f} GB)")

    if exe_bak.exists():
        print(f"  {EXE_NAME} を復元中...")
        shutil.copy2(exe_bak, exe)
        exe_bak.unlink()
        print(f"    完了 ({exe.stat().st_size / (1024**2):.1f} MB)")

    if state_path.exists():
        state_path.unlink()

    print()
    print("=" * 56)
    print("  アンインストール完了!")
    print("=" * 56)
    print()
    print("  ゲームファイルと言語設定を元に戻しました。")
    print()

    return True


def do_uninstall():
    """メイン処理"""
    print_header()

    # モード選択
    mode = ask_mode()

    if mode == 1:
        return do_language_reset()

    # 完全アンインストール: ゲームフォルダが必要
    print("\n  Steam ゲームフォルダを検出中...")
    from . import steam_finder
    game_dir = steam_finder.detect_game_dir()
    if not game_dir:
        print("  エラー: ゲームフォルダが見つかりません。")
        return False
    print(f"  検出: {game_dir}")

    return do_full_uninstall(game_dir)


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
