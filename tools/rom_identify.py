#!/usr/bin/env python3
"""Identifica o sistema de uma ROM (extensão + magic bytes + cabeçalhos) e opcionalmente a salva em docs/orig/.

Uso:
  rom_identify.py <rom> [--copy-to docs/orig]

Saída: JSON em stdout com hashes, candidatos de sistema (ordenados por confiança) e metadados.
Com --copy-to, copia a ROM sem modificá-la e grava <dir>/rom-info.json.
Sem dependências além da biblioteca padrão (Python 3.8+).
"""
import argparse
import hashlib
import json
import os
import shutil
import sys
import zlib

EXT_MAP = {
    ".nes": "NES", ".fds": "Famicom Disk System", ".unf": "NES", ".unif": "NES",
    ".sfc": "SNES", ".smc": "SNES", ".fig": "SNES", ".swc": "SNES",
    ".gb": "Game Boy", ".gbc": "Game Boy Color", ".cgb": "Game Boy Color",
    ".gba": "Game Boy Advance", ".agb": "Game Boy Advance",
    ".nds": "Nintendo DS", ".dsi": "Nintendo DS", ".3ds": "Nintendo 3DS", ".cia": "Nintendo 3DS",
    ".z64": "Nintendo 64", ".v64": "Nintendo 64", ".n64": "Nintendo 64", ".u64": "Nintendo 64",
    ".gcm": "GameCube", ".rvz": "GameCube/Wii", ".wbfs": "Wii", ".wad": "Wii",
    ".vb": "Virtual Boy", ".vboy": "Virtual Boy",
    ".md": "Sega Genesis / Mega Drive", ".gen": "Sega Genesis / Mega Drive", ".smd": "Sega Genesis / Mega Drive",
    ".32x": "Sega 32X", ".sms": "Sega Master System", ".gg": "Sega Game Gear", ".sg": "SG-1000",
    ".sc": "SC-3000", ".cue": "CD-ROM (ver .bin)", ".chd": "CD/DVD (CHD)",
    ".pce": "PC Engine / TurboGrafx-16", ".sgx": "PC Engine SuperGrafx",
    ".a26": "Atari 2600", ".a52": "Atari 5200", ".a78": "Atari 7800", ".lnx": "Atari Lynx",
    ".j64": "Atari Jaguar", ".jag": "Atari Jaguar", ".st": "Atari ST", ".xex": "Atari 8-bit", ".atr": "Atari 8-bit",
    ".ngp": "Neo Geo Pocket", ".ngc": "Neo Geo Pocket Color", ".neo": "Neo Geo",
    ".ws": "WonderSwan", ".wsc": "WonderSwan Color",
    ".col": "ColecoVision", ".int": "Intellivision", ".vec": "Vectrex",
    ".d64": "Commodore 64", ".prg": "Commodore 64", ".crt": "Commodore 64", ".t64": "Commodore 64",
    ".adf": "Amiga", ".tap": "ZX Spectrum / C64 (fita)", ".tzx": "ZX Spectrum", ".z80": "ZX Spectrum",
    ".sna": "ZX Spectrum", ".dsk": "MSX / Amstrad / Apple II", ".mx1": "MSX", ".mx2": "MSX",
    ".nsp": "Nintendo Switch", ".xci": "Nintendo Switch", ".iso": "Disco óptico (ver conteúdo)",
    ".pbp": "PlayStation / PSP", ".cso": "PSP", ".exe": "PlayStation (PS-X EXE) ou Windows",
    ".zip": "Arquivo compactado (extrair antes)", ".7z": "Arquivo compactado (extrair antes)",
}
AMBIGUOUS_EXT = {".bin", ".rom", ".img", ".dat", ".iso"}


def at(data, off, n):
    return data[off:off + n] if off >= 0 and off + n <= len(data) else b""


def detect(data, ext):
    c = []  # (system, confidence 0-100, reason, extra)

    def add(system, conf, reason, **extra):
        c.append({"system": system, "confidence": conf, "reason": reason, **extra})

    # Containers
    if data[:2] == b"PK":
        add("Arquivo ZIP", 95, "assinatura PK", container=True)
    if data[:6] == b"7z\xbc\xaf\x27\x1c":
        add("Arquivo 7z", 95, "assinatura 7z", container=True)
    if data[:8] == b"MComprHD":
        add("CHD (disco comprimido)", 95, "assinatura MComprHD", container=True)

    # Nintendo
    if data[:4] == b"NES\x1a":
        v2 = (data[7] & 0x0C) == 0x08
        mapper = (data[6] >> 4) | (data[7] & 0xF0)
        add("NES", 99, "cabeçalho iNES" + (" 2.0" if v2 else ""), mapper=mapper,
            prg_16k=data[4], chr_8k=data[5])
    if data[:4] == b"FDS\x1a":
        add("Famicom Disk System", 99, "cabeçalho FDS")
    if data[:4] == b"UNIF":
        add("NES", 95, "cabeçalho UNIF")

    copier = 512 if len(data) % 1024 == 512 else 0
    body = data[copier:]
    for base, name in ((0x7FC0, "LoROM"), (0xFFC0, "HiROM"), (0x40FFC0, "ExHiROM")):
        h = at(body, base, 32)
        if len(h) == 32:
            comp = int.from_bytes(h[28:30], "little")
            csum = int.from_bytes(h[30:32], "little")
            title = h[:21]
            if (comp ^ csum) == 0xFFFF and all(32 <= b < 127 or b in (0, 0x20) for b in title):
                add("SNES", 97, f"checksum válido em {hex(base)} ({name})",
                    title=title.decode("ascii", "replace").strip(), copier_header=bool(copier))
                break

    if at(data, 0x104, 4) == b"\xCE\xED\x66\x66":
        cgb = data[0x143] if len(data) > 0x143 else 0
        title = at(data, 0x134, 16).split(b"\0")[0].decode("ascii", "replace")
        if cgb in (0x80, 0xC0):
            add("Game Boy Color", 97, "logo Nintendo + flag CGB", title=title, cgb_only=cgb == 0xC0)
        else:
            add("Game Boy", 97, "logo Nintendo em 0x104", title=title,
                sgb=len(data) > 0x146 and data[0x146] == 0x03)
    if at(data, 4, 4) == b"\x24\xFF\xAE\x51" and len(data) > 0xB2 and data[0xB2] == 0x96:
        add("Game Boy Advance", 99, "logo Nintendo + 0x96 em 0xB2",
            title=at(data, 0xA0, 12).split(b"\0")[0].decode("ascii", "replace"),
            game_code=at(data, 0xAC, 4).decode("ascii", "replace"))
    if at(data, 0x15C, 2) == b"\x56\xCF":
        add("Nintendo DS", 95, "CRC do logo (0xCF56) em 0x15C", title=at(data, 0, 12).split(b"\0")[0].decode("ascii", "replace"),
            dsi=bool(len(data) > 0x12 and data[0x12] & 2))
    m = data[:4]
    if m == b"\x80\x37\x12\x40":
        add("Nintendo 64", 99, "magic 0x80371240", byte_order="z64 (big-endian)")
    elif m == b"\x37\x80\x40\x12":
        add("Nintendo 64", 99, "magic 0x37804012", byte_order="v64 (byte-swapped)")
    elif m == b"\x40\x12\x37\x80":
        add("Nintendo 64", 99, "magic 0x40123780", byte_order="n64 (little-endian)")
    if at(data, 0x1C, 4) == b"\xC2\x33\x9F\x3D":
        add("GameCube", 99, "magic 0xC2339F3D em 0x1C", game_id=at(data, 0, 6).decode("ascii", "replace"))
    if at(data, 0x18, 4) == b"\x5D\x1C\x9E\xA3":
        add("Wii", 99, "magic 0x5D1C9EA3 em 0x18", game_id=at(data, 0, 6).decode("ascii", "replace"))
    if at(data, 0x100, 4) == b"NCSD":
        add("Nintendo 3DS", 95, "NCSD em 0x100")
    if data[:4] == b"NCCH" or at(data, 0x100, 4) == b"NCCH":
        add("Nintendo 3DS", 90, "NCCH")
    if data[:4] == b"WBFS":
        add("Wii", 90, "WBFS")
    if data[:4] == b"HEAD" or data[:4] == b"PFS0":
        add("Nintendo Switch", 70, "cabeçalho XCI/NSP")

    # Sega
    hdr = at(data, 0x100, 16)
    if hdr[:4] == b"SEGA" or hdr[:4] == b" SEG":
        name = "Sega 32X" if b"32X" in hdr else "Sega Genesis / Mega Drive"
        add(name, 97, "'SEGA' em 0x100",
            title=at(data, 0x120, 48).decode("ascii", "replace").strip(),
            region=at(data, 0x1F0, 3).decode("ascii", "replace").strip())
    for off in (0x7FF0, 0x3FF0, 0x1FF0):
        if at(data, off, 8) == b"TMR SEGA":
            reg = (data[off + 0x0F] >> 4) if len(data) > off + 0x0F else 0
            add("Sega Game Gear" if reg in (5, 6, 7) else "Sega Master System", 95,
                f"'TMR SEGA' em {hex(off)}", region_code=reg)
            break
    for off in (0, 0x10):
        s = at(data, off, 16)
        if s.startswith(b"SEGADISCSYSTEM") or s.startswith(b"SEGA SEGASATURN") or s.startswith(b"SEGA SEGAKATANA"):
            add("Sega CD" if b"DISCSYSTEM" in s else "Saturn" if b"SATURN" in s else "Dreamcast", 90, "cabeçalho de disco Sega")
            break

    # Sony
    if data[:8] == b"PS-X EXE":
        add("PlayStation", 99, "PS-X EXE")
    for off in (0x8000, 0x9318):
        if at(data, off + 1, 5) == b"CD001" or at(data, off + 1, 5) == b"CD001":
            sysid = at(data, off + 8, 32)
            if b"PLAYSTATION" in sysid:
                add("PlayStation", 85, "ISO9660 com system id PLAYSTATION (PS1 ou PS2: checar SYSTEM.CNF)")
            elif b"PSP GAME" in sysid:
                add("PSP", 85, "ISO9660 PSP GAME")
            else:
                add("Imagem ISO9660 genérica", 40, "CD001", system_id=sysid.decode("ascii", "replace").strip())
            break

    # Outros
    if at(data, 1, 9) == b"ATARI7800":
        add("Atari 7800", 99, "cabeçalho A78")
    if data[:4] == b"LYNX":
        add("Atari Lynx", 99, "cabeçalho LYNX")
    if at(data, 0, 16) in (b"COPYRIGHT BY SNK", b" LICENSED BY SNK") or data[:16].startswith(b" LICENSED BY SNK"):
        add("Neo Geo Pocket (Color)", 95, "texto SNK")
    if at(data, 0, 13) == b"C64 CARTRIDGE":
        add("Commodore 64", 99, "cabeçalho CRT")
    if data[:2] == b"AB" and ext in (".rom", ".mx1", ".mx2", ".bin", ""):
        add("MSX", 70, "'AB' no início")
    if data[:2] in (b"\xAA\x55", b"\x55\xAA") and ext in (".col", ".rom", ".bin", ""):
        add("ColecoVision", 55, "marcador AA55/55AA")
    if len(data) >= 16 and data[-10] == 0xEA and ext in (".ws", ".wsc"):
        add("WonderSwan", 85, "footer com JMP FAR")
    if ext in (".a26", ".bin") and len(data) in (2048, 4096, 8192, 12288, 16384, 32768, 65536):
        add("Atari 2600", 60 if ext == ".a26" else 30, f"tamanho {len(data)} compatível com cartuchos 2600")
    if ext == ".pce" and len(data) % 8192 in (0, 512):
        add("PC Engine / TurboGrafx-16", 85, "extensão .pce + tamanho múltiplo de 8 KiB")

    # Extensão como fallback/reforço
    if ext in EXT_MAP:
        known = {x["system"] for x in c}
        if EXT_MAP[ext] not in known and not any(EXT_MAP[ext].split(" /")[0] in k for k in known):
            add(EXT_MAP[ext], 50 if not c else 20, f"extensão {ext}")
        else:
            for x in c:
                if EXT_MAP[ext].split(" /")[0] in x["system"]:
                    x["confidence"] = min(100, x["confidence"] + 1)
                    x["reason"] += f"; extensão {ext} coerente"
    elif ext in AMBIGUOUS_EXT and not c:
        add("Desconhecido", 0, f"extensão {ext} é ambígua e sem assinatura reconhecida")

    c.sort(key=lambda x: -x["confidence"])
    return c


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rom")
    ap.add_argument("--copy-to", help="diretório (ex.: docs/orig) onde copiar a ROM e gravar rom-info.json")
    a = ap.parse_args()

    if not os.path.isfile(a.rom):
        print(json.dumps({"error": f"arquivo não encontrado: {a.rom}"}), file=sys.stderr)
        return 1
    with open(a.rom, "rb") as f:
        data = f.read()
    ext = os.path.splitext(a.rom)[1].lower()
    cands = detect(data, ext)
    best = cands[0] if cands else None
    info = {
        "file": os.path.basename(a.rom),
        "extension": ext,
        "size_bytes": len(data),
        "crc32": f"{zlib.crc32(data) & 0xFFFFFFFF:08x}",
        "md5": hashlib.md5(data).hexdigest(),
        "sha1": hashlib.sha1(data).hexdigest(),
        "sha256": hashlib.sha256(data).hexdigest(),
        "candidates": cands,
        "identified": bool(best and best["confidence"] >= 80 and not best.get("container")),
        "best_guess": best["system"] if best else None,
    }
    if a.copy_to:
        os.makedirs(a.copy_to, exist_ok=True)
        dest = os.path.join(a.copy_to, os.path.basename(a.rom))
        if os.path.abspath(dest) != os.path.abspath(a.rom):
            shutil.copy2(a.rom, dest)
        info["stored_at"] = dest.replace("\\", "/")
        with open(os.path.join(a.copy_to, "rom-info.json"), "w", encoding="utf-8") as f:
            json.dump(info, f, indent=2, ensure_ascii=False)
    print(json.dumps(info, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
