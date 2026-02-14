"""
gpak デルタリパック操作

ベース gpak に overlay ディレクトリの変更ファイルを重ねてリパックする。
mewgenics_mod.py から移植、進捗バー追加。stdlib のみで動作。
"""
import re
import struct
import sys
from pathlib import Path

CHUNK = 8 * 1024 * 1024  # 8MB

EXCLUDE_SUFFIXES = {".orig", ".bak"}
EXCLUDE_NAMES = {".DS_Store", "Thumbs.db"}


def gpak_read_index(f):
    """gpak ファイルの TOC (Table of Contents) を読む"""
    entry_count = struct.unpack("<I", f.read(4))[0]
    entries = []
    for _ in range(entry_count):
        name_len = struct.unpack("<H", f.read(2))[0]
        name = f.read(name_len).decode("utf-8")
        size = struct.unpack("<I", f.read(4))[0]
        entries.append((name, size))
    return entries


def overlay_rename(name):
    """overlay ファイル名を gpak 内の名前にマッピング。
    例: catnames_female_ja.txt → catnames_female_en.txt (ゲームは en のみ読む)"""
    m = re.match(r"(data/catnames_\w+)_ja(\.txt)$", name)
    if m:
        return m.group(1) + "_en" + m.group(2)
    return name


def _progress_bar(current, total, width=40):
    """シンプルな進捗バー表示"""
    pct = current / total if total > 0 else 1.0
    filled = int(width * pct)
    bar = "=" * filled + "-" * (width - filled)
    sys.stdout.write(f"\r  [{bar}] {pct*100:.0f}% ({current}/{total})")
    sys.stdout.flush()


def gpak_repack_delta(base_gpak, overlay_dir, output_gpak, quiet=False):
    """ベース gpak に overlay_dir の変更を重ねてリパック。

    overlay_dir にあるファイルはディスクから読み、
    ないファイル (WAV等) はベース gpak から直接ストリーミング。
    """
    # ベース gpak の TOC を読み、各ファイルのデータオフセットを計算
    with open(base_gpak, "rb") as f:
        base_entries = gpak_read_index(f)
        base_data_start = f.tell()

    base_file_map = {}
    offset = base_data_start
    for name, size in base_entries:
        base_file_map[name] = (offset, size)
        offset += size

    # overlay ディレクトリのファイルをスキャン
    overlay_files = {}
    for path in sorted(overlay_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() in EXCLUDE_SUFFIXES:
            continue
        if path.name in EXCLUDE_NAMES or path.name.startswith("._"):
            continue
        name = str(path.relative_to(overlay_dir)).replace("\\", "/")
        packed_name = overlay_rename(name)
        if packed_name != name:
            overlay_files[packed_name] = path
        elif re.match(r"data/catnames_\w+_en\.txt$", name):
            ja_name = name.replace("_en.txt", "_ja.txt")
            ja_path = overlay_dir / Path(ja_name)
            if ja_path.exists():
                continue
            overlay_files[name] = path
        else:
            overlay_files[name] = path

    # ファイルリスト構築: ベース順を維持 + overlay 新規ファイルを末尾に追加
    final = []
    seen = set()

    for name, _ in base_entries:
        seen.add(name)
        if name in overlay_files:
            p = overlay_files[name]
            final.append(("overlay", name, p, p.stat().st_size))
        else:
            bo, bs = base_file_map[name]
            final.append(("base", name, bo, bs))

    for name in sorted(overlay_files):
        if name not in seen:
            p = overlay_files[name]
            final.append(("overlay", name, p, p.stat().st_size))

    from_base = sum(1 for e in final if e[0] == "base")
    from_overlay = sum(1 for e in final if e[0] == "overlay")
    if not quiet:
        print(f"  {len(final)} ファイル ({from_overlay} 翻訳 + {from_base} ベース)")

    # 出力 gpak 書き込み
    total_data = sum(e[3] for e in final)
    written = 0

    with open(output_gpak, "wb") as out:
        # TOC 書き込み
        out.write(struct.pack("<I", len(final)))
        for entry in final:
            name_bytes = entry[1].encode("utf-8")
            out.write(struct.pack("<H", len(name_bytes)))
            out.write(name_bytes)
            out.write(struct.pack("<I", entry[3]))

        # データ書き込み
        with open(base_gpak, "rb") as base_f:
            for i, entry in enumerate(final):
                size = entry[3]
                if entry[0] == "overlay":
                    with open(entry[2], "rb") as src:
                        remaining = size
                        while remaining > 0:
                            chunk = src.read(min(remaining, CHUNK))
                            out.write(chunk)
                            written += len(chunk)
                            remaining -= len(chunk)
                else:
                    base_f.seek(entry[2])
                    remaining = size
                    while remaining > 0:
                        chunk = base_f.read(min(remaining, CHUNK))
                        out.write(chunk)
                        written += len(chunk)
                        remaining -= len(chunk)

                if not quiet:
                    _progress_bar(i + 1, len(final))

    if not quiet:
        total_size = output_gpak.stat().st_size
        print(f"\n  完了! ({total_size / (1024*1024*1024):.2f} GB)")

    return True
