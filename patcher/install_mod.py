"""
Mewgenics 日本語MOD インストーラー

7ステップでゲームに日本語MODを適用する:
1. Steam ゲームフォルダ自動検出
2. ゲーム実行中チェック
3. ゲームバージョン確認
4. バックアップ作成
5. gpak デルタリパック
6. exe ZWSP パッチ
7. 状態保存
"""
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent
OVERLAY_DIR = ROOT_DIR / "overlay"

# 設定読み込み
with open(SCRIPT_DIR / "config.json", "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

EXE_NAME = CONFIG["exe_name"]
GPAK_NAME = CONFIG["gpak_name"]
BACKUP_SUFFIX = CONFIG["backup_suffix"]
STATE_FILE = CONFIG["state_file"]


def print_header():
    print()
    print("=" * 56)
    print("  Mewgenics 日本語MOD インストーラー")
    print(f"  バージョン {CONFIG['mod_version']}")
    print("=" * 56)
    print()


def is_game_running(game_dir):
    """exe がロックされているか (ゲーム実行中) 確認"""
    exe = game_dir / EXE_NAME
    if not exe.exists():
        return False
    try:
        f = open(exe, "r+b")
        f.close()
        return False
    except (PermissionError, OSError):
        return True


def check_disk_space(game_dir):
    """ディスク空き容量をチェック"""
    gpak = game_dir / GPAK_NAME
    if not gpak.exists():
        return True, ""

    gpak_size = gpak.stat().st_size
    # バックアップ + 一時ファイル分の容量が必要
    required = gpak_size + 500 * 1024 * 1024  # gpak + 500MB

    try:
        usage = shutil.disk_usage(game_dir)
        if usage.free < required:
            free_gb = usage.free / (1024 ** 3)
            need_gb = required / (1024 ** 3)
            return False, (
                f"ディスク空き容量が不足しています\n"
                f"    必要: {need_gb:.1f} GB / 空き: {free_gb:.1f} GB"
            )
    except OSError:
        pass  # 容量チェック失敗は無視して続行

    return True, ""


def check_version(game_dir):
    """exe/gpak サイズをテスト済みバージョンと照合"""
    warnings = []

    exe = game_dir / EXE_NAME
    if exe.exists():
        exe_size = exe.stat().st_size
        tested_exe = CONFIG["tested_versions"]["exe_sizes"]
        if tested_exe and exe_size not in tested_exe:
            warnings.append(
                f"    exe サイズ ({exe_size:,} bytes) が未テスト版です\n"
                f"    テスト済み: {', '.join(str(s) for s in tested_exe)}"
            )

    gpak = game_dir / GPAK_NAME
    if gpak.exists():
        gpak_size = gpak.stat().st_size
        tested_gpak = CONFIG["tested_versions"]["gpak_sizes"]
        if tested_gpak and gpak_size not in tested_gpak:
            warnings.append(
                f"    gpak サイズ ({gpak_size:,} bytes) が未テスト版です"
            )

    return warnings


def load_state(game_dir):
    """インストール状態を読み込む"""
    state_path = game_dir / STATE_FILE
    if state_path.exists():
        try:
            return json.loads(state_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_state(game_dir, gpak_size, exe_size=None):
    """インストール状態を保存"""
    state = {
        "mod_version": CONFIG["mod_version"],
        "installed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "gpak_backup_size": gpak_size,
    }
    if exe_size:
        state["exe_backup_size"] = exe_size

    state_path = game_dir / STATE_FILE
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def create_backups(game_dir):
    """gpak と exe のバックアップを作成"""
    gpak = game_dir / GPAK_NAME
    gpak_bak = game_dir / (GPAK_NAME + BACKUP_SUFFIX)
    exe = game_dir / EXE_NAME
    exe_bak = game_dir / (EXE_NAME + BACKUP_SUFFIX)

    created = False

    # 既存バックアップの整合性チェック
    state = load_state(game_dir)

    if gpak_bak.exists():
        # バックアップと現在の gpak を比較
        # ゲーム更新でgpakが変わっていたらバックアップを更新
        if state.get("gpak_backup_size") and gpak.stat().st_size != state.get("gpak_backup_size"):
            # 現在のgpakサイズがバックアップ時と異なる → ゲーム更新された
            # バックアップのサイズを確認
            if gpak_bak.stat().st_size == state.get("gpak_backup_size"):
                # バックアップは古い。gpakは更新済み(MOD未適用)なのでバックアップ更新
                print("    ゲーム更新を検出: バックアップを更新します...")
                shutil.copy2(gpak, gpak_bak)
                created = True
        print("    gpak バックアップ: 既存を使用")
    else:
        print("    gpak バックアップを作成中...")
        shutil.copy2(gpak, gpak_bak)
        created = True
        print(f"    {gpak_bak.name} ({gpak_bak.stat().st_size / (1024**3):.2f} GB)")

    if exe_bak.exists():
        # exe更新チェック: 現在のexeにZWSPシグネチャがないなら未パッチ=新しいバニラexe
        from . import exe_patcher
        if not exe_patcher.is_patched(exe):
            # 現在のexeはバニラ → バックアップを更新
            if state.get("exe_backup_size") and exe.stat().st_size != state.get("exe_backup_size"):
                print("    exe 更新を検出: バックアップを更新します...")
                shutil.copy2(exe, exe_bak)
                created = True
        print("    exe バックアップ: 既存を使用")
    else:
        print("    exe バックアップを作成中...")
        shutil.copy2(exe, exe_bak)
        created = True
        print(f"    {exe_bak.name} ({exe_bak.stat().st_size / (1024**2):.1f} MB)")

    return gpak_bak, exe_bak, created


def do_install():
    """メインインストール処理"""
    print_header()

    # --- [1/7] Steam ゲームフォルダ自動検出 ---
    print("[1/7] Steam ゲームフォルダを検出中...")
    from . import steam_finder
    game_dir = steam_finder.detect_game_dir()
    if not game_dir:
        print("\n  エラー: ゲームフォルダが見つかりません。")
        print("  インストールを中止します。")
        return False

    print(f"  検出: {game_dir}")

    # ファイル存在確認
    exe_path = game_dir / EXE_NAME
    gpak_path = game_dir / GPAK_NAME
    if not exe_path.exists():
        print(f"\n  エラー: {EXE_NAME} が見つかりません: {exe_path}")
        return False
    if not gpak_path.exists():
        print(f"\n  エラー: {GPAK_NAME} が見つかりません: {gpak_path}")
        return False

    # --- [2/7] ゲーム実行中チェック ---
    print("\n[2/7] ゲーム実行状態を確認中...")
    if is_game_running(game_dir):
        print("  エラー: ゲームが実行中です。")
        print("  ゲームを終了してから再度実行してください。")
        return False
    print("  OK")

    # --- [3/7] ゲームバージョン確認 ---
    print("\n[3/7] ゲームバージョンを確認中...")
    warnings = check_version(game_dir)
    if warnings:
        print("  注意: 未テストバージョンのゲームです。")
        for w in warnings:
            print(w)
        print()
        ans = input("  続行しますか? (Y/n): ").strip().lower()
        if ans == "n":
            print("  インストールを中止しました。")
            return False
    else:
        print("  OK")

    # --- [4/7] バックアップ作成 ---
    print("\n[4/7] バックアップを作成中...")
    ok, msg = check_disk_space(game_dir)
    if not ok:
        print(f"  エラー: {msg}")
        return False

    gpak_bak, exe_bak, _ = create_backups(game_dir)

    # --- [5/7] gpak デルタリパック ---
    print("\n[5/7] 翻訳データを適用中...")
    if not OVERLAY_DIR.exists():
        print(f"  エラー: overlay ディレクトリが見つかりません: {OVERLAY_DIR}")
        return False

    from . import gpak_ops

    # gpak.tmp に書き込み → アトミックリネーム
    gpak_tmp = game_dir / (GPAK_NAME + ".tmp")
    try:
        gpak_ops.gpak_repack_delta(gpak_bak, OVERLAY_DIR, gpak_tmp)

        # アトミックリネーム (Windows では上書きリネームに os.replace を使用)
        os.replace(gpak_tmp, gpak_path)
    except Exception as e:
        # 失敗時は tmp ファイルを削除
        if gpak_tmp.exists():
            gpak_tmp.unlink()
        print(f"\n  エラー: gpak リパック失敗: {e}")
        return False

    # --- [6/7] exe ZWSP パッチ ---
    print("\n[6/7] ワードラップパッチを適用中...")
    from . import exe_patcher

    success, msg = exe_patcher.apply_patch(exe_path, exe_bak)
    if success:
        print(f"  {msg}")
    else:
        print(f"  警告: exe パッチ失敗: {msg}")
        print("  翻訳は動作しますが、長文テキストの改行が不自然になる場合があります。")

    # --- [7/7] 状態保存 ---
    print("\n[7/7] インストール状態を保存中...")
    save_state(
        game_dir,
        gpak_size=gpak_bak.stat().st_size,
        exe_size=exe_bak.stat().st_size if exe_bak.exists() else None,
    )
    print("  OK")

    # 完了メッセージ
    print()
    print("=" * 56)
    print("  インストール完了!")
    print("=" * 56)
    print()
    print("  ゲームを起動して以下の手順で日本語に切り替えてください:")
    print("    Settings → Language → 日本語")
    print()

    return True


def main():
    try:
        success = do_install()
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
