# The falsifier: silentfail run on code it has never seen

The corpus proves the linter does what its author designed. It cannot prove the linter is right about
code its author never wrote - the corpus was written by the same person who wrote the rules. This is
the test that attacks that, and it is the one the README promises.

## Method

Five public repositories, shallow-cloned, pinned at the commit each was cloned at, scanned at the
default confidence floor (`high`). Every finding above that floor was then read in context and
adjudicated by hand into one of three verdicts:

- **deliberate** - the code does what it means to do, and the pattern is the idiom for it
- **possible defect** - the code looks wrong on its own terms
- **false positive** - the linter is wrong about what the code does

## Result, 2026-10-19

| repository | files walked | high | medium | low |
|---|---|---|---|---|
| pallets/flask | 236 | **0** | 0 | 0 |
| psf/requests | 128 | **0** | 0 | 0 |
| python-poetry/poetry | 987 | **0** | 1 | 0 |
| dokku/dokku | 1,814 | **0** | 7 | 0 |
| scrapy/scrapy | 735 | **0** | 1 | 1 |
| **total** | **3,900** | **0** | 9 | 1 |
| *CPython standard library* | *2,417* | *14 -> 0* | *1* | *7* |

**Zero high-confidence findings across 3,900 files of other people's Python and shell.** The tool
made no accusation at the floor it runs at by default.

## The nine maybes, adjudicated

| finding | verdict |
|---|---|
| dokku `bootstrap.sh:259`, `image/healthcheck.sh:19,31,66`, `unit/test_helper.bash:34,48,228` | **deliberate** - `cmd || true` is the cleanup idiom: `docker rm -f`, `rm -f`, `docker logs`. Swallowed on purpose, and the rule says so at `medium` rather than calling it a defect |
| poetry `.github/scripts/backport.sh:31` | **possible defect** - `done \|\| : GETOPT="${GETOPT:=getopt}"`. The colon builtin takes that assignment as an *argument*, so it does not assign; if the loop above fails to find GNU getopt, `GETOPT` stays unset and the next line runs `--test` from an empty expansion. Looks like a real (small) latent bug. |
| scrapy `core/downloader/tls.py:157` | **false positive** - `if depth != 0: return True` is a guard clause that only verifies the leaf certificate, with the reason written in the comment above it. Reported at `medium`, not at the default floor. |
| scrapy `utils/project.py:43` | **false positive** - an `os.walk` in a file that mentions `SCRAPY_SETTINGS_MODULE`; the rule is looking for a scanner that matches its own text and found only a name. `low`. |

## The sixth sample: the CPython standard library, and 14 false positives

2,417 files, 157 s, **14 high-confidence findings** - and every one of them was wrong. Two
misreadings, each fixed:

| what the linter said | what the code does |
|---|---|
| 11 x `record-unread`: "declares `ABORT` and no line of this file reads it" (`tkinter/messagebox.py`, `test/pickletester.py`, `test/support/__init__.py`, ...) | these are **exported values**, read by importers. The rule requires a `__main__` guard to mean "script, not library", and these modules satisfy it with a demo block. The rule now also requires the value to look like a file path, which is what a record is. |
| 3 x `check-cannot-fail`: "tests for `%` in `tmp_value` after `tmp_value` was normalised to remove it" (`configparser.py` x2, `sysconfig/__main__.py`) | `value.replace("%%", "")` strips **escaped pairs**; a bare `%` survives and the guard fires exactly as designed. A doubled pattern removes pairs, not the character. Fixed. |

After both fixes: 2,417 files, **0 high findings**, and the corpus still certifies 46/46 with zero
false positives. Four new self-test fixtures pin the behaviour in both directions.

This is the most useful result in the file. The corpus could not have found these - it was written
by the same person who wrote the rules. Only a large body of code written by other people could.

## Two more defects the falsifier found in the tool

1. **A branch that raises was reported as a silent pass.** poetry's `scripts/check_argv0.py` raises
   `RuntimeError` on every failing path; the rule only looked for a `return`, so a check that
   cannot fail silently was accused. Fixed: a `raise` in the branch counts as signalling. Fixture
   `branch-that-raises-quiet` added.
2. **The evidence string was a 12-character slice.** dokku's finding read
   `a failure is swallowed with || ull 2>&1 || true` - unusable. Fixed to quote the clause that is
   being swallowed. Fixture `swallowed-failure-quotes-the-command` added.

Both fixes are in `v0.1.2`; the self-test went from 40 to 42 checks because of them.

## What this does not prove

**Recall on stranger code is not measured here.** There is no ground truth on these repositories -
finding nothing at the default floor is consistent both with "the tool is quiet" and with "the tool
is blind", and only a labelled defect set can tell those apart. What is measured is the half the
kill criterion was about: does it accuse innocent code. At this sample, no.

## Performance

Speed is fine on shell and poor on Python, measured rather than guessed:

| sample | files | seconds |
|---|---|---|
| dokku (shell) | 1,814 | 0.59 |
| CPython standard library (Python) | 2,417 | 142 before, 89 after |

A profile of the 2,273 Python files, per rule, at v0.1.5:

| rule | seconds |
|---|---|
| `check-cannot-fail` (Python) | 60 |
| `dead-guard` | 58 |
| `unread-constant` | 20 |
| `control-reads-own-text` | 14 |
| `test-replaces-subject` | 8 |
| `record-unread` | 6 |
| `printed-check` | 0.6 |

`dead-guard` walked the whole scope subtree once per function, so it was quadratic in functions per
file; `check-cannot-fail` walks the tree several times per file.

## The cache that did not help, and the assumption behind it

**A parse cache was added and did not move the total (137 s to 134 s), and I wrote that down as
"parsing was not the cost". That conclusion was wrong, and the way it was wrong is worth keeping.**
Counting calls instead of guessing: the scan made **4,365 `ast.parse` calls for 2,273 files**, and
2,499 of them were re-parsing a file the scan had already opened. The cache cleared itself above
1,200 files, which is *below* the size of the corpus being measured, so every later pass began cold.
A cache that evicts its own working set looks exactly like a cache that was never needed.

Two changes, each measured separately:

| | `ast.parse` calls | wall | peak resident |
|---|---|---|---|
| v0.1.5 | 4,365 | 142.3 s | 1,283 MB |
| v0.1.6, the three cross-file rules collect per file instead of re-iterating | **1,866** | **89.1 s** | **275 MB** |

Peak resident was sampled every 1.2 s from outside the process, because the in-process API for it
returned zero on this platform and a memory number nobody measured is a memory number nobody has.

The three cross-file rules (`record-unread`, `test-replaces-subject`, `dead-guard`) answer
questions that span files, so they still decide last - but they now take one file's facts at the
moment that file is open, instead of re-opening all 2,273 files afterwards. `dead-guard` no longer
keeps every parse tree alive; it keeps the small facts the decision actually needs.

**A 48 MB byte-budget cache was also measured and rejected.** It reached the same 1,866 parses but
sat at 890 MB resident and 1,414 MB peak - worse than the 1,283 MB the refactor had just removed -
because an AST is an order of magnitude larger than its source. One pass per file is cheaper than
holding the corpus. The linter runs on the same machine as the things it checks, so 275 MB against
1,283 MB is not a detail.

Findings were byte-identical before and after on nine corpora (flask, requests, poetry, dokku,
scrapy, this repository, memory-conformance, retained, a 102-finding estate tree), and the
self-test and the 105-case corpus stayed green - the refactor is only worth anything if the
answers did not move.
