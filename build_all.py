#!/usr/bin/env python3
"""Build all PaliVerse Dictionary data files and a manifest.

Usage: build_all.py DPD_DB CST_ROMN_DIR OUT_DIR

Reads sets.json (collection -> CST file stems). Writes OUT_DIR/<set>.json and OUT_DIR/manifest.json.
"""
import datetime
import glob
import hashlib
import json
import os
import sys

import build_data

HERE = os.path.dirname(os.path.abspath(__file__))


def main(db, cst_dir, out_dir):
    sets = json.load(open(os.path.join(HERE, "sets.json"), encoding="utf-8"))
    os.makedirs(out_dir, exist_ok=True)
    manifest = {"format": 1, "built": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "source": "Digital Pāḷi Dictionary by Bodhirasa Bhikkhu, https://www.dpdict.net/",
                "licence": "CC BY-NC-SA 4.0", "cst_commit": os.environ.get("CST_COMMIT", ""), "files": {}}
    for name, stems in sets.items():
        paths = []
        for stem in stems:
            hits = sorted(glob.glob(os.path.join(cst_dir, stem + ".*.xml")))
            if len(hits) != 1:
                sys.exit(f"{name}: expected exactly one CST file for {stem}, found {hits}")
            paths.append(hits[0])
        out = os.path.join(out_dir, name + ".json")
        stats = build_data.main(db, out, paths)
        manifest["dpd"] = stats.pop("version")
        data = open(out, "rb").read()
        stats.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                     coverage=round(100.0 * stats["distinct_found"] / stats["distinct"], 3))
        manifest["files"][name + ".json"] = stats
        print(name, stats, flush=True)
    with open(os.path.join(out_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
