#!/usr/bin/env python3
"""Build one PaliVerse Dictionary data file from the DPD database and CST source texts.

Usage: build_data.py DPD_DB OUT_JSON CST_XML [CST_XML ...]

Output: {"v": DPD release, "forms": {form: [headword ids, grammar, deconstructor]}, "hw": {id: entry}}
Data: Digital Pāḷi Dictionary by Bodhirasa Bhikkhu, CC BY-NC-SA 4.0 (https://www.dpdict.net/).
"""
import json
import re
import sqlite3
import sys

L = "a-zāīūṅñṭḍṇḷṃ"
SH = {"ā": "a", "ī": "i", "ū": "u"}
TOKEN = re.compile(rf"[{L}]+(?:'[{L}]+)*")


def text(xml):
    xml = re.sub(r"<note>.*?</note>", "", xml, flags=re.S)
    return re.sub(r"<[^>]+>", " ", xml)


def norm(s):
    s = s.lower().replace("ṁ", "ṃ").replace("’", "'").replace("‘", "'")
    return re.sub(r"'+", "'", s)


def cand(t):
    """Spellings to try for a token; tokens with an apostrophe (e.g. dhamma'nti) are joined words."""
    if "'" not in t:
        return [t]
    h = t.split("'")[0]
    out = [t.replace("'", ""), h]
    if h[-1:] in SH:
        out.append(h[:-1] + SH[h[-1]])
    out.append(h + "ṃ")
    return out


def loads(s):
    return json.loads(s) if s else []


def main(db_path, out_path, xml_paths):
    con = sqlite3.connect(db_path)
    version = con.execute("select value from db_info where key='dpd_release_version'").fetchone()[0]

    tokens = set()
    total = 0
    for p in xml_paths:
        toks = TOKEN.findall(norm(text(open(p, encoding="utf-16").read())))
        total += len(toks)
        tokens.update(toks)

    def lookup(key):
        r = con.execute("select headwords, grammar, deconstructor from lookup where lookup_key=?", (key,)).fetchone()
        if not r:
            return None
        e = [loads(r[0]), loads(r[1]), loads(r[2])]
        return e if (e[0] or e[2]) else None

    forms = {}
    for t in sorted(tokens):
        for c in cand(t):
            if c in forms:
                continue
            e = lookup(c)
            if e:
                forms[c] = e
    # parts of the first deconstruction, so the card can show each part with its meaning
    for key in list(forms):
        dec = forms[key][2]
        if dec:
            for part in (x.strip() for x in dec[0].split("+")):
                if part and part not in forms:
                    e = lookup(part)
                    if e:
                        forms[part] = e

    ids = sorted({i for e in forms.values() for i in e[0]})
    hw = {}
    fields = (("l", "lemma_1"), ("p", "pos"), ("m", "meaning_1"), ("g", "grammar"), ("lit", "meaning_lit"),
              ("c", "construction"), ("r", "root_key"), ("ct", "compound_type"), ("n", "ebt_count"), ("pc", "plus_case"))
    cols = ", ".join(f for _, f in fields) + ", meaning_2"
    for i in ids:
        r = con.execute(f"select {cols} from dpd_headwords where id=?", (i,)).fetchone()
        if not r:
            continue
        d = {}
        for (k, _), v in zip(fields, r):
            if k == "m" and not v:
                v = r[-1]  # entries without a finished meaning use DPD's second meaning field
            if isinstance(v, str):
                v = re.sub(r"<[^>]+>", "", v)  # DPD marks sound changes with <b>…</b>
            if v not in ("", None, 0):
                d[k] = v
        hw[str(i)] = d

    found = sum(1 for t in tokens if any(c in forms for c in cand(t)))
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"v": version, "forms": dict(sorted(forms.items())), "hw": hw}, f, ensure_ascii=False, separators=(",", ":"))
    return {"version": version, "words": total, "distinct": len(tokens), "distinct_found": found,
            "forms": len(forms), "headwords": len(hw)}


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    print(json.dumps(main(sys.argv[1], sys.argv[2], sys.argv[3:]), ensure_ascii=False))
