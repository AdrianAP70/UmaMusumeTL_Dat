#!/usr/bin/env python3
import json, os, sys, hashlib, time
from pathlib import Path

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "localized_data" 
OUT_FILE = ROOT / "index.json"

EXCLUDE_REL = {
    "includes", 
    "config.json",
}

def sha256_of(path: Path, bufsize=1024 * 1024):
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(bufsize)
            if not b:
                break
            h.update(b)
    return h.hexdigest()

def main():
    if not DATA_DIR.is_dir():
        print(f"[ERR] Folder {DATA_DIR} tidak ditemukan.", file=sys.stderr)
        sys.exit(1)

    files = []
    total_size = 0

    for p in DATA_DIR.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(DATA_DIR).as_posix()
        # exclude spesifik
        if rel in EXCLUDE_REL:
            continue
        # opsional: skip file/folder diawali '#'
        parts = Path(rel).parts
        if any(str(s).startswith("#") for s in parts):
            continue

        size = p.stat().st_size
        digest = sha256_of(p)
        files.append({"path": rel, "sha256": digest, "size": size})
        total_size += size

    files.sort(key=lambda x: x["path"])

    payload = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "base_path": "localized_data/",
        "file_count": len(files),
        "total_size": total_size,
        "files": files,
    }

    OUT_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] Wrote {OUT_FILE} with {len(files)} files.")

if __name__ == "__main__":
    main()
