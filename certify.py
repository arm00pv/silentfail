#!/usr/bin/env python3
"""certify.py - plant the corpus in a throwaway directory, scan it, and score the linter.

This is the whole claim in one command. The corpus ships WITH the tool so that a reader does not
have to believe a number in a README: 46 planted defects must all be found, and 59 correct
subsystems that look suspicious must produce no findings at all. Any miss or any false positive
exits non-zero.

  python certify.py                 # certificate at the default floor (high)
  python certify.py --floor=medium  # the aggressive rules, which are maybes by design
  python certify.py --verbose       # per-class table and every row
"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import silentfail as sf                                              # noqa: E402

RANK = {"low": 0, "medium": 1, "high": 2}
TOLERANCE = 3


def load():
    # THE CORPUS IS A MODULE, not a data file, so that it travels inside the installed wheel:
    # a tool whose certificate only runs in its own checkout is a tool whose numbers you have
    # to take on faith.
    import corpus_data
    return {"cases": corpus_data.CASES, "truth": corpus_data.TRUTH}


def plant(root, corpus):
    written = 0
    for case, files in corpus["cases"].items():
        for name, body in files.items():
            p = os.path.join(root, case, name)
            parent = os.path.dirname(p)
            if parent:
                os.makedirs(parent, exist_ok=True)
            with open(p, "w", encoding="utf-8", newline=chr(10)) as fh:
                fh.write(body)
            written += 1
    return written


def score(floor="high", verbose=False):
    corpus = load()
    root = tempfile.mkdtemp(prefix="silentfail_corpus_")
    try:
        files = plant(root, corpus)
        findings, skipped, walked = sf.scan([root])
        findings = [f for f in findings if RANK.get(f.get("confidence"), 0) >= RANK[floor]]
        by_case = {}
        for f in findings:
            rel = os.path.relpath(f["file"], root).replace(chr(92), "/")
            by_case.setdefault(rel.split("/")[0], []).append(f)
        rows, misses, false_positives = [], [], []
        for case in sorted(corpus["truth"]):
            t = corpus["truth"][case]
            got = by_case.get(case, [])
            if t["expect"] == "clean":
                false_positives.extend(got)
                rows.append((case, "clean", "ok" if not got else "FALSE-POSITIVE", len(got), t))
                continue
            also = [os.path.basename(x) for x in (t.get("also") or [])]
            hit = [f for f in got
                   if f["class"] == t["class"]
                   and ((os.path.basename(f["file"]) == os.path.basename(t["file"])
                         and t["line"] is not None
                         and abs(f["line"] - t["line"]) <= TOLERANCE)
                        or os.path.basename(f["file"]) in also)]
            if not hit:
                misses.append(t)
            rows.append((case, t["class"], "hit" if hit else "MISS", len(got), t))
        defects = [r for r in rows if r[1] != "clean"]
        clean = [r for r in rows if r[1] == "clean"]
        hits = [r for r in defects if r[2] == "hit"]
        print("corpus: %d case(s) - %d defect, %d clean near-miss   files planted: %d   walked: %d"
              % (len(rows), len(defects), len(clean), files, walked))
        print("recall: %d/%d = %.0f%%" % (len(hits), len(defects),
                                           100.0 * len(hits) / max(1, len(defects))))
        print("false positives: %d finding(s) on %d clean case(s)" % (len(false_positives), len(clean)))
        per = {}
        for r in defects:
            d = per.setdefault(r[1], [0, 0])
            d[1] += 1
            d[0] += 1 if r[2] == "hit" else 0
        for cls in sorted(per):
            h, n = per[cls]
            print("  %-24s %d/%d" % (cls, h, n))
        for case, cls, outcome, n, t in rows:
            if outcome in ("MISS", "FALSE-POSITIVE"):
                print("  %-16s %-24s %s (%d finding(s)) file=%s line=%s"
                      % (case, cls, outcome, n, t.get("file"), t.get("line")))
            elif verbose:
                print("  %-16s %-24s %s" % (case, cls, outcome))
        bad = bool(misses) or bool(false_positives)
        print("VERDICT: %s" % ("CERTIFIED" if not bad else "DENIED"))
        return 0 if not bad else 1
    finally:
        shutil.rmtree(root, ignore_errors=True)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    floor = "high"
    for a in argv:
        if a.startswith("--floor="):
            floor = a.split("=", 1)[1]
    if floor not in RANK:
        print("REFUSING: unknown floor %r" % floor)
        return 2
    return score(floor=floor, verbose="--verbose" in argv)


if __name__ == "__main__":
    sys.exit(main())
