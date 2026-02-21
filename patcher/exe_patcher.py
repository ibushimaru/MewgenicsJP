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


def _has_fullwidth_space_check(data, idx, text_start, text_end):
    """近傍に全角スペース (0x3000) の比較命令があるか確認"""
    search_start = max(text_start, idx - 0x40)
    search_end = min(text_end, idx + 0x40)
    # cmp dx, 0x3000 (即値)
    if data.find(bytes.fromhex("6681fa0030"), search_start, search_end) != -1:
        return True
    # mov eax, 0x3000 / cmp dx, ax (レジスタ経由)
    if data.find(bytes.fromhex("b800300000"), search_start, search_end) != -1:
        return True
    return False


def _find_patch3(data, text_start, text_end, text_section):
    """Patch 3: cmp dx, 0x20 + jne short を検索

    パターン: 66 83 fa 20  75 XX
    条件: 近傍 (前後 0x40 バイト) に 0x3000 (全角スペース) 比較が存在
    """
    CMP_DX_20 = bytes.fromhex("6683fa20")

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
            if _has_fullwidth_space_check(data, idx, text_start, text_end):
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


def _find_code_caves(data, text_start, text_end, sizes=(25, 25, 23)):
    """text セクション内のゼロパディング領域からコードケーブを確保

    各トランポリンに必要なサイズ: T1=25, T2=25, T3=23 bytes
    連続73byte以上のケーブが1つあればそこに全部配置。
    なければ個別に確保して分散配置する。
    """
    total = sum(sizes)

    # 全てのゼロパディング領域を列挙
    caves = []
    run_start = 0
    run_len = 0
    for i in range(text_start, text_end):
        if data[i] == 0:
            if run_len == 0:
                run_start = i
            run_len += 1
        else:
            if run_len >= min(sizes):
                caves.append((run_start, run_len))
            run_len = 0
    if run_len >= min(sizes):
        caves.append((run_start, run_len))

    # 方法1: 1つの大きな領域に全て配置
    for start, size in caves:
        if size >= total + 1:  # +1 for safety margin
            return [(start + 1, sizes[0]), (start + 1 + sizes[0], sizes[1]),
                    (start + 1 + sizes[0] + sizes[1], sizes[2])]

    # 方法2: 分散配置 (各トランポリンを別々の領域に)
    allocated = []
    used = set()
    for needed in sizes:
        found = False
        for start, size in sorted(caves, key=lambda x: -x[1]):
            # 既に使用した領域と重ならないか
            cave_start = start + 1
            cave_end = cave_start + needed
            if size < needed + 1:
                continue
            overlap = False
            for a_start, a_size in used:
                if not (cave_end <= a_start or cave_start >= a_start + a_size):
                    overlap = True
                    break
            if not overlap:
                allocated.append((cave_start, needed))
                used.add((cave_start, needed))
                found = True
                break
        if not found:
            return None

    return allocated


def _build_trampoline_r9w(cave_va, true_target, false_target):
    """r9w トランポリン: r9w == 0x20 || r9w == 0x200B を判定 (25 bytes)"""
    code = bytearray()
    code += b'\x66\x41\x83\xf9\x20'      # cmp r9w, 0x20
    code += b'\x74\x06'                    # je .is_space
    code += b'\x66\x41\x81\xf9\x0b\x20'  # cmp r9w, 0x200B
    code += b'\x75\x05'                    # jne .not_space
    is_va = cave_va + len(code)
    code += b'\xe9' + _rel32(is_va, true_target)
    not_va = cave_va + len(code)
    code += b'\xe9' + _rel32(not_va, false_target)
    return bytes(code)


def _build_trampoline_dx(cave_va, true_target, false_target):
    """dx トランポリン: dx == 0x20 || dx == 0x200B を判定 (23 bytes)"""
    code = bytearray()
    code += b'\x66\x83\xfa\x20'           # cmp dx, 0x20
    code += b'\x74\x05'                    # je .is_space
    code += b'\x66\x81\xfa\x0b\x20'      # cmp dx, 0x200B
    code += b'\x75\x05'                    # jne .not_space
    is_va = cave_va + len(code)
    code += b'\xe9' + _rel32(is_va, true_target)
    not_va = cave_va + len(code)
    code += b'\xe9' + _rel32(not_va, false_target)
    return bytes(code)


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

    # コードケーブ確保 (分散配置対応)
    caves = _find_code_caves(data, text_start, text_end)
    if not caves:
        return False, "コードケーブ (ゼロパディング領域) が不足しています"

    c1_fo, c1_size = caves[0]
    c2_fo, c2_size = caves[1]
    c3_fo, c3_size = caves[2]
    c1_va = _fo_to_va(c1_fo, text)
    c2_va = _fo_to_va(c2_fo, text)
    c3_va = _fo_to_va(c3_fo, text)

    # トランポリンコード構築
    t1_code = _build_trampoline_r9w(c1_va, patch1["fallthrough_va"], patch1["jne_target_va"])
    t2_code = _build_trampoline_r9w(c2_va, patch2["je_target_va"], patch2["fallthrough_va"])
    t3_code = _build_trampoline_dx(c3_va, patch3["fallthrough_va"], patch3["jne_target_va"])

    # バックアップ
    if backup_path and not Path(backup_path).exists():
        Path(backup_path).write_bytes(bytes(data))

    # Patch 1: jmp to trampoline 1 + nops
    p1_bytes = b'\xe9' + _rel32(patch1["va"], c1_va) + b'\x90' * 6
    data[patch1["fo"]:patch1["fo"] + 11] = p1_bytes

    # Patch 2: jmp to trampoline 2 + nops
    p2_bytes = b'\xe9' + _rel32(patch2["va"], c2_va) + b'\x90' * 6
    data[patch2["fo"]:patch2["fo"] + 11] = p2_bytes

    # Patch 3: jmp to trampoline 3 + nop
    p3_bytes = b'\xe9' + _rel32(patch3["va"], c3_va) + b'\x90'
    data[patch3["fo"]:patch3["fo"] + 6] = p3_bytes

    # コードケーブ書き込み
    data[c1_fo:c1_fo + len(t1_code)] = t1_code
    data[c2_fo:c2_fo + len(t2_code)] = t2_code
    data[c3_fo:c3_fo + len(t3_code)] = t3_code

    # 書き込み
    Path(exe_path).write_bytes(bytes(data))

    cave_total = len(t1_code) + len(t2_code) + len(t3_code)
    msg = (
        f"パッチ適用完了 (3箇所 + トランポリン {cave_total} bytes)\n"
        f"    Patch 1: VA 0x{patch1['va']:x} → Cave FO 0x{c1_fo:x}\n"
        f"    Patch 2: VA 0x{patch2['va']:x} → Cave FO 0x{c2_fo:x}\n"
        f"    Patch 3: VA 0x{patch3['va']:x} → Cave FO 0x{c3_fo:x}"
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
