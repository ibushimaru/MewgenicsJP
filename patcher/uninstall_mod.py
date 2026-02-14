"""
Mewgenics 日本語MOD アンインストーラー

バックアップからゲームファイルを復元する。
"""
import json
import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

with open(SCRIPT_DIR / "config.json", "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

EXE_NAME = CONFIG["exe_name"]
GPAK_NAME = CONFIG["gpak_name"]
BACKUP_SUFFIX = CONFIG["backup_suffix"]
STATE_FILE = CONFIG["state_file"]


def print_header():
    print()
    print("=" * 56)
    print("  Mewgenics 日本語MOD アンインストーラー")
    print("=" * 56)
    print()


def do_uninstall():
    """アンインストール処理"""
    print_header()

    # ゲームフォルダ検出
    print("[1/3] Steam ゲームフォルダを検出中...")
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
    print("\n[2/3] ゲーム実行状態を確認中...")
    try:
        f = open(exe, "r+b")
        f.close()
    except (PermissionError, OSError):
        print("  エラー: ゲームが実行中です。")
        print("  ゲームを終了してから再度実行してください。")
        return False
    print("  OK")

    # 復元
    print("\n[3/3] ゲームファイルを復元中...")
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

    input("  Enter キーを押して終了...")
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
