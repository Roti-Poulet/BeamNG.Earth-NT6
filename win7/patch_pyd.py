"""Windows 7 / Vista: make Rust-built extension modules (server/earthfast.pyd) loadable.

Those modules import three things that only exist on newer Windows:
    bcryptprimitives.dll              ProcessPrng                                   (Windows 10)
    api-ms-win-core-synch-l1-2-0.dll  WaitOnAddress, WakeByAddressSingle/All        (Windows 8)
This script rewrites the DLL names in the .pyd's import table to "efw7shim.dll" (win7/efw7shim.dll, source:
efw7shim.c), which exports the same functions. It is idempotent and safe to run before every start; a
release update that brings a fresh .pyd is simply patched again. The original is kept as <name>.orig.

    python win7/patch_pyd.py            patch every .pyd of the BeamNG.Earth folder (not python/)
    python win7/patch_pyd.py FILE...    patch the given files
"""
import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SHIM = "efw7shim.dll"
REPLACE = {"bcryptprimitives.dll", "api-ms-win-core-synch-l1-2-0.dll"}


def rva_to_off(sections, rva):
    for va, vsize, raw, rsize in sections:
        if va <= rva < va + max(vsize, rsize):
            return rva - va + raw
    return None


def patch(path):
    with open(path, "rb") as f:
        data = bytearray(f.read())
    if data[:2] != b"MZ":
        return "not a PE file"
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe:pe + 4] != b"PE\0\0":
        return "not a PE file"
    nsec, = struct.unpack_from("<H", data, pe + 6)
    optsize, = struct.unpack_from("<H", data, pe + 20)
    opt = pe + 24
    magic, = struct.unpack_from("<H", data, opt)
    dd = opt + (112 if magic == 0x20B else 96)          # data directories
    imp_rva, imp_size = struct.unpack_from("<II", data, dd + 8)
    if not imp_rva:
        return "no imports"
    sec = opt + optsize
    sections = []
    for i in range(nsec):
        vsize, va, rsize, raw = struct.unpack_from("<IIII", data, sec + 40 * i + 8)
        sections.append((va, vsize, raw, rsize))
    off = rva_to_off(sections, imp_rva)
    changed = []
    while off is not None:
        oft, _ts, _fc, name_rva, _ft = struct.unpack_from("<IIIII", data, off)
        if not name_rva and not oft:
            break
        noff = rva_to_off(sections, name_rva)
        end = data.index(b"\0", noff)
        name = bytes(data[noff:end]).decode("ascii", "replace")
        if name.lower() in REPLACE:
            if len(SHIM) > end - noff:
                return "import name too short to patch: " + name
            data[noff:end] = SHIM.encode("ascii") + b"\0" * (end - noff - len(SHIM))
            changed.append(name)
        off += 20
    if not changed:
        return "already patched or nothing to patch"
    bound_rva, _ = struct.unpack_from("<II", data, dd + 11 * 8)
    if bound_rva:                                        # bound imports would hide the new names
        struct.pack_into("<II", data, dd + 11 * 8, 0, 0)
    bak = path + ".orig"
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
    tmp = path + ".new"
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, path)
    return "patched (" + ", ".join(changed) + ")"


def main(argv):
    shim_src = os.path.join(HERE, SHIM)
    if not os.path.isfile(shim_src):
        print("[win7] %s is missing next to patch_pyd.py" % SHIM)
        return 1
    targets = argv[1:]
    if not targets:
        for base, dirs, files in os.walk(ROOT):
            dirs[:] = [d for d in dirs if d.lower() not in ("python", ".git", "win7")]
            targets += [os.path.join(base, n) for n in files if n.lower().endswith(".pyd")]
    folders = {os.path.join(ROOT, "python")}
    for t in targets:
        try:
            res = patch(t)
        except Exception as e:                           # never block the start because of this
            res = "error: %r" % (e,)
        print("[win7] %s: %s" % (os.path.relpath(t, ROOT), res))
        folders.add(os.path.dirname(os.path.abspath(t)))
    for d in folders:                                    # the shim next to the Python and next to each module
        dst = os.path.join(d, SHIM)
        try:
            if os.path.isdir(d) and (not os.path.exists(dst) or os.path.getsize(dst) != os.path.getsize(shim_src)):
                shutil.copy2(shim_src, dst)
        except OSError as e:
            print("[win7] could not copy %s to %s: %s" % (SHIM, d, e))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
