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

**Zero high-confidence findings across 3,900 files of other people's Python and shell.** The tool
made no accusation at the floor it runs at by default.

## The nine maybes, adjudicated

| finding | verdict |
|---|---|
| dokku `bootstrap.sh:259`, `image/healthcheck.sh:19,31,66`, `unit/test_helper.bash:34,48,228` | **deliberate** - `cmd || true` is the cleanup idiom: `docker rm -f`, `rm -f`, `docker logs`. Swallowed on purpose, and the rule says so at `medium` rather than calling it a defect |
| poetry `.github/scripts/backport.sh:31` | **possible defect** - `done \|\| : GETOPT="${GETOPT:=getopt}"`. The colon builtin takes that assignment as an *argument*, so it does not assign; if the loop above fails to find GNU getopt, `GETOPT` stays unset and the next line runs `--test` from an empty expansion. Looks like a real (small) latent bug. |
| scrapy `core/downloader/tls.py:157` | **false positive** - `if depth != 0: return True` is a guard clause that only verifies the leaf certificate, with the reason written in the comment above it. Reported at `medium`, not at the default floor. |
| scrapy `utils/project.py:43` | **false positive** - an `os.walk` in a file that mentions `SCRAPY_SETTINGS_MODULE`; the rule is looking for a scanner that matches its own text and found only a name. `low`. |

## Two defects the falsifier found in the tool

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

Speed is fine on shell (`dokku`, 1,814 files, 0.59 s) and poor on Python: the standard library needs
more than a minute per two thousand files, with single large files such as `test_inspect.py` taking
1.7 s. Per-file cost is dominated by repeated whole-file scans inside the Python rules; that is the
next performance item, not a design limit.
