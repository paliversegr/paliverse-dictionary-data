#!/usr/bin/env python3
"""Check a finished build before it is published, and write the release notes.

Usage: check_build.py OUT_DIR EXPECTED_DPD_TAG [PREVIOUS_MANIFEST]

Fails (exit 1) if a file is missing, the DPD version is not the expected one, any collection is
below MIN_COVERAGE, or any collection lost more than TOLERANCE percentage points against the
previous release.
"""
import json
import os
import sys

MIN_COVERAGE = 90.0
TOLERANCE = 0.1


def main(out_dir, tag, prev_path=None):
    sets = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "sets.json"), encoding="utf-8"))
    m = json.load(open(os.path.join(out_dir, "manifest.json"), encoding="utf-8"))
    prev = json.load(open(prev_path, encoding="utf-8")) if prev_path and os.path.exists(prev_path) else None
    problems = []
    if m.get("dpd") != tag:
        problems.append(f"database says {m.get('dpd')}, expected {tag}")
    rows = []
    for name in sets:
        f = name + ".json"
        s = m["files"].get(f)
        if not s or not os.path.exists(os.path.join(out_dir, f)):
            problems.append(f"{f} is missing")
            continue
        old = (prev or {}).get("files", {}).get(f)
        if s["coverage"] < MIN_COVERAGE:
            problems.append(f"{f}: coverage {s['coverage']}% is below {MIN_COVERAGE}%")
        if old and s["coverage"] < old["coverage"] - TOLERANCE:
            problems.append(f"{f}: coverage fell from {old['coverage']}% to {s['coverage']}%")
        change = f"{s['forms'] - old['forms']:+d}" if old else "–"
        rows.append(f"| {name} | {s['distinct']:,} | {s['coverage']:.2f}% | {s['forms']:,} | {change} | {s['headwords']:,} |")
    notes = [f"Dictionary data for PaliVerse, built from the Digital Pāḷi Dictionary release **{tag}**.", ""]
    if prev:
        notes += [f"Compared with {prev.get('dpd')}.", ""]
    notes += ["| Collection | Distinct words in the text | Found | Forms in the file | Change | Headwords |",
              "|---|---|---|---|---|---|"] + rows
    notes += ["", "Data: Digital Pāḷi Dictionary by Bodhirasa Bhikkhu, https://www.dpdict.net/, CC BY-NC-SA 4.0. "
              "Shared here under the same licence. Source texts: Chaṭṭha Saṅgāyana (CST) edition."]
    with open(os.path.join(out_dir, "notes.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(notes) + "\n")
    print("\n".join(notes))
    if problems:
        print("\nNOT PUBLISHED:\n- " + "\n- ".join(problems), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    sys.exit(main(*sys.argv[1:4]))
