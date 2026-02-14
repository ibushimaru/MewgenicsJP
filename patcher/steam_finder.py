"""
Steam ゲームフォルダ自動検出

Windowsレジストリ → libraryfolders.vdf → Mewgenics フォルダ検索
"""
import os
import re
from pathlib import Path

# Mewgenics の Steam App ID
APP_ID = "1920960"
GAME_DIR_NAME = "Mewgenics"


def find_steam_install_path():
    """レジストリから Steam のインストールパスを取得"""
    try:
        import winreg
        for key_path in [
            r"SOFTWARE\Valve\Steam",
            r"SOFTWARE\WOW6432Node\Valve\Steam",
        ]:
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
                value, _ = winreg.QueryValueEx(key, "InstallPath")
                winreg.CloseKey(key)
                if value and Path(value).exists():
                    return Path(value)
            except (OSError, FileNotFoundError):
                continue
    except ImportError:
        pass

    # レジストリ失敗時のフォールバック
    for candidate in [
        Path(os.environ.get("ProgramFiles(x86)", "")) / "Steam",
        Path(os.environ.get("ProgramFiles", "")) / "Steam",
        Path("C:/Program Files (x86)/Steam"),
        Path("C:/Program Files/Steam"),
    ]:
        if candidate.exists():
            return candidate

    return None


def parse_libraryfolders_vdf(vdf_path):
    """libraryfolders.vdf をパースしてライブラリパスのリストを返す"""
    paths = []
    try:
        text = vdf_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return paths

    # VDFフォーマット: "path" "C:\\Program Files (x86)\\Steam"
    for m in re.finditer(r'"path"\s+"([^"]+)"', text):
        p = Path(m.group(1).replace("\\\\", "\\"))
        if p.exists():
            paths.append(p)

    # path キーが見つからない場合、数字キーで直接パスを指定する古い形式
    if not paths:
        for m in re.finditer(r'"\d+"\s+"([^"]+)"', text):
            val = m.group(1).replace("\\\\", "\\")
            p = Path(val)
            if p.exists() and (p / "steamapps").exists():
                paths.append(p)

    return paths


def find_game_path():
    """Mewgenics のゲームフォルダを自動検出して返す。見つからなければ None。"""
    steam_path = find_steam_install_path()
    if not steam_path:
        return None

    # ライブラリフォルダの一覧を取得
    library_paths = [steam_path]  # メインの Steam フォルダ

    vdf = steam_path / "steamapps" / "libraryfolders.vdf"
    if vdf.exists():
        extra = parse_libraryfolders_vdf(vdf)
        for p in extra:
            if p not in library_paths:
                library_paths.append(p)

    # 各ライブラリから Mewgenics を探す
    for lib in library_paths:
        game_dir = lib / "steamapps" / "common" / GAME_DIR_NAME
        if game_dir.exists() and (game_dir / "Mewgenics.exe").exists():
            return game_dir

    return None


def ask_user_path():
    """ユーザーにゲームフォルダのパスを入力してもらう"""
    print()
    print("  Mewgenics のゲームフォルダが見つかりませんでした。")
    print("  手動でパスを入力してください。")
    print()
    print("  確認方法:")
    print("    Steam → Mewgenics → 右クリック → 管理")
    print("    → ローカルファイルを閲覧")
    print()

    while True:
        path_str = input("  ゲームフォルダのパス: ").strip().strip('"')
        if not path_str:
            return None

        game_dir = Path(path_str)
        if not game_dir.exists():
            print(f"  エラー: フォルダが見つかりません: {game_dir}")
            continue

        if not (game_dir / "Mewgenics.exe").exists():
            # もしかして steamapps/common まで指定した?
            sub = game_dir / GAME_DIR_NAME
            if sub.exists() and (sub / "Mewgenics.exe").exists():
                game_dir = sub
            else:
                print(f"  エラー: Mewgenics.exe が見つかりません: {game_dir}")
                print(f"  例: D:\\SteamLibrary\\steamapps\\common\\Mewgenics")
                continue

        return game_dir


def detect_game_dir():
    """ゲームフォルダを検出する (自動 → 手動入力フォールバック)"""
    game_dir = find_game_path()
    if game_dir:
        return game_dir
    return ask_user_path()
