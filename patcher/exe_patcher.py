"""
Mewgenics.exe ZWSP ワードラップパッチ (パターン検索方式)

ゲームエンジンのワードラップ判定 (スペース U+0020 のみ) に
ZWSP (U+200B) を追加する。これにより日本語テキストに ZWSP を
挿入して改行ポイントを制御できる。

パッチ概要:
- Patch 1: cmp r9w, 0x20 + jne → ZWSP も改行ポイントとして認識
- Patch 2: cmp r9w, 0x20 + je  → ZWSP もスペースとして扱う
- Patch 3: cmp dx, 0x20 + jne short → 行頭 ZWSP 自動削除
- コードケーブ: .text 末尾の 00 パディングにトランポリンコードを配置

パターン検索方式: ハードコードアドレスを使わず、バイトパターンで
パッチ位置を動的に特定する。ゲームアップデートに耐性がある。
"""
import struct
from pathlib import Path


# パッチ適用済み検知用シグネチャ
ZWSP_SIGNATURE = bytes.fromhex("664181f90b20")  # cmp r9w, 0x200B


def _parse_pe_sections(data):
    """PE ヘッダーを解析して .text セクションの情報を返す"""
    # DOS header → PE offset
    if data[:2] != b"MZ":
        raise ValueError("MZ ヘッダーがありません")

    pe_offset = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe_offset:pe_offset + 4] != b"PE\x00\x00":
        raise ValueError("PE シグネチャがありません")

    # COFF header
    coff = pe_offset + 4
    num_sections = struct.unpack_from("<H", data, coff + 2)[0]
    optional_size = struct.unpack_from("<H", data, coff + 16)[0]

    # Optional header → ImageBase
    opt = coff + 20
    magic = struct.unpack_from("<H", data, opt)[0]
    if magic == 0x20B:  # PE32+
        image_base = struct.unpack_from("<Q", data, opt + 24)[0]
    else:
        image_base = struct.unpack_from("<I", data, opt + 28)[0]

    # Section headers
    section_start = opt + optional_size
    sections = {}
    for i in range(num_sections):
        off = section_start + i * 40
        name = data[off:off + 8].rstrip(b"\x00").decode("ascii", errors="replace")
        virt_size = struct.unpack_from("<I", data, off + 8)[0]
        virt_addr = struct.unpack_from("<I", data, off + 12)[0]
        raw_size = struct.unpack_from("<I", data, off + 16)[0]
        raw_addr = struct.unpack_from("<I", data, off + 20)[0]
        sections[name] = {
            "virt_addr": image_base + virt_addr,
            "virt_size": virt_size,
            "raw_addr": raw_addr,
            "raw_size": raw_size,
        }

    return image_base, sections


def _va_to_fo(va, text_section):
    """VA (Virtual Address) → File Offset"""
    return va - text_section["virt_addr"] + text_section["raw_addr"]


def _fo_to_va(fo, text_section):
    """File Offset → VA"""
    return fo - text_section["raw_addr"] + text_section["virt_addr"]


def _rel32(from_va, to_va):
    """jmp/jcc 用の 32bit 相対アドレスを計算"""
    return struct.pack("<i", to_va - (from_va + 5))


def _find_pattern(data, pattern, start, end, description=""):
    """指定範囲でバイトパターンを検索。一意なマッチを返す。"""
    results = []
    pos = start
    while pos < end:
        idx = data.find(pattern, pos, end)
        if idx == -1:
            break
        results.append(idx)
        pos = idx + 1

    if len(results) == 0:
        return None
    if len(results) > 1 and description:
        # 複数マッチは許可しない (安全策)
        return None
    return results[0]


def _find_patch1(data, text_start, text_end, text_section):
    """Patch 1: cmp r9w, 0x20 + jne (near) を検索

    パターン: 66 41 83 f9 20  0f 85 XX XX XX XX
    条件: jne のオフセットが 0x0050-0x0200 の範囲 (妥当な距離)
    """
    CMP_R9W_20 = bytes.fromhex("664183f920")
    JNE_NEAR = bytes.fromhex("0f85")

    pos = text_start
    candidates = []
    while pos < text_end:
        idx = data.find(CMP_R9W_20, pos, text_end)
        if idx == -1:
            break
        # 直後に 0f 85 (jne near) があるか
        jne_pos = idx + 5
        if jne_pos + 6 <= text_end and data[jne_pos:jne_pos + 2] == JNE_NEAR:
            rel = struct.unpack_from("<i", data, jne_pos + 2)[0]
            # jne のターゲットが妥当な範囲内か
            if 0x0050 <= rel <= 0x0200:
                jne_target_va = _fo_to_va(jne_pos, text_section) + 6 + rel
                fallthrough_va = _fo_to_va(jne_pos, text_section) + 6
                candidates.append({
                    "fo": idx,
                    "va": _fo_to_va(idx, text_section),
                    "size": 11,  # 5 (cmp) + 6 (jne near)
                    "jne_target_va": jne_target_va,
                    "fallthrough_va": fallthrough_va,
                })
        pos = idx + 1

    if len(candidates) != 1:
        return None
    return candidates[0]


def _find_patch2(data, text_start, text_end, text_section):
    """Patch 2: cmp r9w, 0x20 + je (near) を検索

    パターン: 66 41 83 f9 20  0f 84 XX XX XX XX
    条件: je のオフセットが 0x0100-0x0400 の範囲
    """
    CMP_R9W_20 = bytes.fromhex("664183f920")
    JE_NEAR = bytes.fromhex("0f84")

    pos = text_start
    candidates = []
    while pos < text_end:
        idx = data.find(CMP_R9W_20, pos, text_end)
        if idx == -1:
            break
        jne_pos = idx + 5
        if jne_pos + 6 <= text_end and data[jne_pos:jne_pos + 2] == JE_NEAR:
            rel = struct.unpack_from("<i", data, jne_pos + 2)[0]
            if 0x0100 <= rel <= 0x0400:
                je_target_va = _fo_to_va(jne_pos, text_section) + 6 + rel
                fallthrough_va = _fo_to_va(jne_pos, text_section) + 6
                candidates.append({
                    "fo": idx,
                    "va": _fo_to_va(idx, text_section),
                    "size": 11,
                    "je_target_va": je_target_va,
                    "fallthrough_va": fallthrough_va,
                })
        pos = idx + 1

    if len(candidates) != 1:
        return None
    return candidates[0]


def _find_patch3(data, text_start, text_end, text_section):
    """Patch 3: cmp dx, 0x20 + jne short を検索

    パターン: 66 83 fa 20  75 XX
    条件: 近傍 (前後 0x40 バイト) に cmp dx, 0x3000 (66 81 fa 00 30) が存在
    """
    CMP_DX_20 = bytes.fromhex("6683fa20")
    CMP_DX_3000 = bytes.fromhex("6681fa0030")

    pos = text_start
    candidates = []
    while pos < text_end:
        idx = data.find(CMP_DX_20, pos, text_end)
        if idx == -1:
            break
        # 直後に 75 XX (jne short) があるか
        jne_pos = idx + 4
        if jne_pos + 2 <= text_end and data[jne_pos] == 0x75:
            rel = struct.unpack_from("<b", data, jne_pos + 1)[0]
            jne_target_va = _fo_to_va(jne_pos, text_section) + 2 + rel
            fallthrough_va = _fo_to_va(jne_pos, text_section) + 2

            # 近傍に全角スペース比較があるか確認
            search_start = max(text_start, idx - 0x40)
            search_end = min(text_end, idx + 0x40)
            if data.find(CMP_DX_3000, search_start, search_end) != -1:
                candidates.append({
                    "fo": idx,
                    "va": _fo_to_va(idx, text_section),
                    "size": 6,  # 4 (cmp) + 2 (jne short)
                    "jne_target_va": jne_target_va,
                    "fallthrough_va": fallthrough_va,
                })
        pos = idx + 1

    if len(candidates) != 1:
        return None
    return candidates[0]


def _find_code_cave(data, text_start, text_end, min_size=76):
    """text セクション末尾のゼロパディングからコードケーブを確保"""
    # 末尾から逆方向にゼロ領域を探す
    end = text_start + min(len(data) - text_start, text_end - text_start)
    pos = end - 1
    while pos >= text_start and data[pos] == 0:
        pos -= 1
    zero_start = pos + 1
    zero_size = end - zero_start

    if zero_size < min_size:
        return None

    # 安全マージン: ゼロ領域の先頭から 16 バイト空けてアラインメント確保
    cave_start = zero_start + 16
    cave_start = (cave_start + 15) & ~15  # 16バイトアライン
    available = end - cave_start

    if available < min_size:
        return None

    return cave_start


def _build_cave_code(cave_fo, patch1, patch2, patch3, text_section):
    """3つのトランポリンを含むコードケーブを構築"""
    cave_va = _fo_to_va(cave_fo, text_section)
    code = bytearray()

    # --- Trampoline 1 (Patch 1: cmp r9w, 0x20 / jne) ---
    # r9w == 0x20 → fallthrough (改行ポイント保存)
    # r9w == 0x200B → fallthrough
    # それ以外 → jne_target (スキップ)
    t1_va = cave_va

    code += b'\x66\x41\x83\xf9\x20'      # cmp r9w, 0x20
    code += b'\x74\x06'                    # je .is_space1
    code += b'\x66\x41\x81\xf9\x0b\x20'  # cmp r9w, 0x200B
    code += b'\x75\x05'                    # jne .not_space1
    # .is_space1:
    is_space1_va = t1_va + len(code)
    code += b'\xe9' + _rel32(is_space1_va, patch1["fallthrough_va"])
    # .not_space1:
    not_space1_va = t1_va + len(code)
    code += b'\xe9' + _rel32(not_space1_va, patch1["jne_target_va"])

    t1_size = len(code)

    # --- Trampoline 2 (Patch 2: cmp r9w, 0x20 / je) ---
    # r9w == 0x20 → je_target (スペース処理)
    # r9w == 0x200B → je_target
    # それ以外 → fallthrough (続行)
    t2_va = t1_va + t1_size
    t2_off = len(code)

    code += b'\x66\x41\x83\xf9\x20'      # cmp r9w, 0x20
    code += b'\x74\x06'                    # je .is_space2
    code += b'\x66\x41\x81\xf9\x0b\x20'  # cmp r9w, 0x200B
    code += b'\x75\x05'                    # jne .not_space2
    # .is_space2:
    is_space2_va = t2_va + (len(code) - t2_off)
    code += b'\xe9' + _rel32(is_space2_va, patch2["je_target_va"])
    # .not_space2:
    not_space2_va = t2_va + (len(code) - t2_off)
    code += b'\xe9' + _rel32(not_space2_va, patch2["fallthrough_va"])

    # --- Trampoline 3 (Patch 3: cmp dx, 0x20 / jne) ---
    # dx == 0x20 → fallthrough (行頭スペース/ZWSP削除)
    # dx == 0x200B → fallthrough
    # それ以外 → jne_target
    t3_va = cave_va + len(code)
    t3_off = len(code)

    code += b'\x66\x83\xfa\x20'           # cmp dx, 0x20
    code += b'\x74\x05'                    # je .is_space3
    code += b'\x66\x81\xfa\x0b\x20'      # cmp dx, 0x200B
    code += b'\x75\x05'                    # jne .not_space3
    # .is_space3:
    is_space3_va = t3_va + (len(code) - t3_off)
    code += b'\xe9' + _rel32(is_space3_va, patch3["fallthrough_va"])
    # .not_space3:
    not_space3_va = t3_va + (len(code) - t3_off)
    code += b'\xe9' + _rel32(not_space3_va, patch3["jne_target_va"])

    return bytes(code), t1_va, t2_va, t3_va


def is_patched(exe_path):
    """exe にパッチが既に適用されているか判定"""
    with open(exe_path, "rb") as f:
        data = f.read()
    return ZWSP_SIGNATURE in data


def apply_patch(exe_path, backup_path=None):
    """exe に ZWSP パッチを適用する。

    Returns:
        (True, message) on success
        (False, message) on failure
    """
    data = bytearray(Path(exe_path).read_bytes())

    # 既にパッチ済みか確認
    if ZWSP_SIGNATURE in data:
        return True, "パッチ適用済み (スキップ)"

    # PE ヘッダー解析
    try:
        image_base, sections = _parse_pe_sections(data)
    except ValueError as e:
        return False, f"PE 解析エラー: {e}"

    if ".text" not in sections:
        return False, ".text セクションが見つかりません"

    text = sections[".text"]
    text_start = text["raw_addr"]
    text_end = text_start + text["raw_size"]

    # パッチ位置を検索
    patch1 = _find_patch1(data, text_start, text_end, text)
    if not patch1:
        return False, "Patch 1 のパターンが見つかりません (cmp r9w, 0x20 + jne)"

    patch2 = _find_patch2(data, text_start, text_end, text)
    if not patch2:
        return False, "Patch 2 のパターンが見つかりません (cmp r9w, 0x20 + je)"

    patch3 = _find_patch3(data, text_start, text_end, text)
    if not patch3:
        return False, "Patch 3 のパターンが見つかりません (cmp dx, 0x20 + jne near 0x3000)"

    # コードケーブ確保
    cave_fo = _find_code_cave(data, text_start, text_end)
    if not cave_fo:
        return False, "コードケーブ (ゼロパディング領域) が不足しています"

    # トランポリンコード構築
    cave_code, t1_va, t2_va, t3_va = _build_cave_code(
        cave_fo, patch1, patch2, patch3, text
    )

    # バックアップ
    if backup_path and not Path(backup_path).exists():
        Path(backup_path).write_bytes(bytes(data))

    # Patch 1: jmp to trampoline 1 + nops
    p1_bytes = b'\xe9' + _rel32(patch1["va"], t1_va) + b'\x90' * 6
    data[patch1["fo"]:patch1["fo"] + 11] = p1_bytes

    # Patch 2: jmp to trampoline 2 + nops
    p2_bytes = b'\xe9' + _rel32(patch2["va"], t2_va) + b'\x90' * 6
    data[patch2["fo"]:patch2["fo"] + 11] = p2_bytes

    # Patch 3: jmp to trampoline 3 + nop
    p3_bytes = b'\xe9' + _rel32(patch3["va"], t3_va) + b'\x90'
    data[patch3["fo"]:patch3["fo"] + 6] = p3_bytes

    # コードケーブ書き込み
    data[cave_fo:cave_fo + len(cave_code)] = cave_code

    # 書き込み
    Path(exe_path).write_bytes(bytes(data))

    msg = (
        f"パッチ適用完了 (3箇所 + コードケーブ {len(cave_code)} bytes)\n"
        f"    Patch 1: VA 0x{patch1['va']:x}\n"
        f"    Patch 2: VA 0x{patch2['va']:x}\n"
        f"    Patch 3: VA 0x{patch3['va']:x}\n"
        f"    Cave:    FO 0x{cave_fo:x}"
    )
    return True, msg


def restore_exe(exe_path, backup_path):
    """バックアップから exe を復元"""
    backup = Path(backup_path)
    if not backup.exists():
        return False, "バックアップが見つかりません"

    import shutil
    shutil.copy2(backup, exe_path)
    return True, "exe を復元しました"
