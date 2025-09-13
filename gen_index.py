#!/usr/bin/env python3
import json, os, sys, hashlib
from pathlib import Path

# --- Konfigurasi dasar ---
ROOT = Path(__file__).parent
DATA_DIR = ROOT / "localized_data" 
OUT_FILE = ROOT / "index.json"

EXCLUDE_EXACT = {
    "includes",
    "config.json", 
    ".gitignore", 
}

# Abaikan entri/folder yang diawali '#'
def is_hashable(path: Path) -> bool:
    parts = path.parts
    return not any(p.startswith("#") for p in parts)

def sha256_hex(p: Path, bufsize=1024*1024) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        while True:
            b = f.read(bufsize)
            if not b:
                break
            h.update(b)
    return h.hexdigest()

def build_urls():
    """
    Susun base_url, zip_url, zip_dir.
    Di GitHub Actions tersedia env:
      - GITHUB_REPOSITORY = "owner/repo"
      - GITHUB_REF_NAME   = "main" (nama branch)
    Jika dijalankan lokal, fallback ke owner/repo/branch manual.
    """
    owner_repo = os.environ.get("GITHUB_REPOSITORY", "").strip()
    branch = os.environ.get("GITHUB_REF_NAME", "").strip()

    if not owner_repo:
        # fallback lokal — ganti sesuai repo kamu jika mau
        owner_repo = "AdrianAP70/UmaMusumeTL_Dat"
    if not branch:
        branch = "main"

    owner, repo = owner_repo.split("/", 1)
    base_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/localized_data"
    zip_url  = f"https://codeload.github.com/{owner}/{repo}/zip/refs/heads/{branch}"
    zip_dir  = f"{repo}-{branch}/localized_data"
    return base_url, zip_url, zip_dir

def main():
    if not DATA_DIR.is_dir():
        print(f"[ERR] Folder '{DATA_DIR}' tidak ditemukan.", file=sys.stderr)
        sys.exit(1)

    files = []
    for p in DATA_DIR.rglob("*"):
        if not p.is_file():
            continue

        rel = p.relative_to(DATA_DIR)  # path relatif terhadap localized_data/
        rel_posix = rel.as_posix()

        # skip nama tepat (di root localized_data) & skip item yang diawali '#'
        if rel_posix in EXCLUDE_EXACT:
            continue
        if not is_hashable(rel):
            continue

        size = p.stat().st_size
        digest = sha256_hex(p)

        files.append({
            "path": rel_posix,
            "hash": digest,   # pakai kunci 'hash' (SHA-256) sesuai index resmi
            "size": size
        })

    # urutkan stabil
    files.sort(key=lambda x: x["path"])

    base_url, zip_url, zip_dir = build_urls()
    payload = {
        "base_url": base_url,
        "zip_url":  zip_url,
        "zip_dir":  zip_dir,
        "files":    files
    }

    OUT_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] index.json ditulis: {OUT_FILE} (files={len(files)})")

if __name__ == "__main__":
    main()
