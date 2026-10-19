# silentfail

**Find the four defect classes that make a system lie while reporting success.**

[![ci](https://github.com/arm00pv/silentfail/actions/workflows/ci.yml/badge.svg)](https://github.com/arm00pv/silentfail/actions/workflows/ci.yml)

Nothing crashes. Nothing pages. The job reports success, the check prints a pass, the ledger says
it wrote the row. The failure is silent, so it is discovered weeks later by a person who trusted it.

silentfail is a linter for exactly that shape of bug. No model, no network, no dependencies: one
Python file that scans your Python and POSIX shell and exits non-zero when it finds one.

```
$ silentfail ./scripts
silentfail: 1 finding(s)
./scripts/nightly.sh:2: [check-cannot-fail] the failure branch exits 0: nobody downstream can
tell it failed (high)
(1 file(s) scanned, 0 skipped by size or exclusion)
```

## The four classes

| class | what it looks like | why it survives review |
|---|---|---|
| `check-cannot-fail` | a check whose failure path still returns success, or whose condition an earlier guard already guaranteed | the failure branch looks deliberate; the status is never contradicted |
| `control-reads-own-text` | a scan whose root contains the pattern it scans for | the alarm is always red, so within a week nobody reads it |
| `record-unread` | a record written to a path no reader opens | the writer is correct, and the row exists — it is just never read back |
| `test-replaces-subject` | a test that substitutes a stand-in for the thing under test | the test is real, it just cannot observe the failure it names |

Supporting detectors sharpen the same classes: guards whose condition is a constant, constants
never read, checks whose result is printed and never decided on, and shell pipelines whose exit
status is masked by a trailing `tail`/`sort` under `set -e` without `pipefail`.

## The numbers, and how to reproduce them

```
$ python certify.py
corpus: 105 case(s) - 46 defect, 59 clean near-miss   files planted: 218   walked: 218
recall: 46/46 = 100%
false positives: 0 finding(s) on 59 clean case(s)
  check-cannot-fail        19/19
  control-reads-own-text    6/6
  record-unread            12/12
  test-replaces-subject     9/9
VERDICT: CERTIFIED
```

That command plants the corpus in a temporary directory, scans it, and scores the result against
truth contracts that ship in this repository. Any miss and any false positive exits non-zero — the
numbers above are not a benchmark we ran once, they are the gate you can run in a second.

- **105 cases: 46 planted defects, 59 clean near-misses.** The clean cases are the point. They are
  correct code that looks suspicious: a quota predicate, a label parser returning `None`, a writer
  and reader that agree because one module owns the path, a scanner that excludes itself. A linter
  that finds everything and accuses correct code is the same product failure as a reviewer that
  always says yes, in the opposite direction.
- **40 self-checks** (`python silentfail.py --selftest`), because every rule in this file once
  shipped unable to fire on the very case it was written for. Each detector is falsified in both
  directions: it must fire on the planted defect and stay quiet on the near-miss.
- **Measured against a real audit.** On a 575-file tool tree, an independent frontier reviewer
  returned 90 findings. silentfail covers 56/56 of the plain defects in that set and 74/84 = 88% of
  the claims that survived adjudication. The rest are judgement calls (a backup kept for a human is
  not a bug) and six claims a reproduction disproved. That evaluation set is not shipped here
  because it is one estate's code, but the adjudication method is described in the write-up.

## Use it

```
pip install .            # or: pip install git+https://github.com/arm00pv/silentfail
silentfail path/to/tree
silentfail --json path/to/tree
silentfail --min-confidence=medium path/to/tree   # more findings, more maybes
silentfail --selftest                             # prove the rules still work
```

Exit status is `0` with no findings, `1` with findings, `2` when it refuses to run.

The corpus ships inside the package (`corpus_data.py`), so `silentfail --selftest` and
`python certify.py` work after a plain `pip install`, on a machine that has never seen this
repository.

**pre-commit** — add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/arm00pv/silentfail
    rev: v0.1.0
    hooks:
      - id: silentfail
```

**CI** — one step, no dependencies:

```yaml
      - run: python silentfail.py --selftest
      - run: silentfail src scripts
```

## The limits, plainly

- **Python and POSIX shell only.** No TypeScript, no Go, no YAML.
- **High-confidence by default.** On 3,821 real Python files the high floor returned 410 findings;
  363 of those were medium. A tool that greets you with 363 maybes is a tool you filter out, so the
  aggressive rules are one flag away and honest about being maybes.
- **No autofix.** These bugs need a decision, not a rewrite.
- **Generalisation has a first measurement.** Run cold on 3,900 files of other people's code
  (flask, requests, poetry, dokku, scrapy) it made **zero high-confidence findings** and nine
  `medium` maybes: eight deliberate idioms, one that looks like a real latent bug in a stranger's
  CI script, and two the linter got wrong at `medium`/`low`. Recall on stranger code is still
  unmeasured - there is no ground truth there, and quiet is not the same as correct. Method, file
  counts and every adjudication: [docs/falsifier.md](docs/falsifier.md).
- **Known false-positive families** already fixed and kept as fixtures: report tools that print
  statistics and never decide on them, test files that read a deployed path because reading it is
  the test, and element selectors mistaken for checks.

## The method, if you want to trust the numbers

1. **Truth contracts, not vibes.** Every defect case names its class, file, and the needle inside
   three lines of where the finding must land. Matching the class somewhere else does not count.
2. **Near-miss controls.** Every rule is paired with correct code that resembles the defect.
   A rule that cannot tell them apart is wrong, not conservative.
3. **Both-direction falsification.** A selftest fixture proves the rule fires; a second proves it
   stays quiet. Six rules here shipped without that and were caught by it afterwards.
4. **A pre-registered kill criterion.** A linter that accuses correct code is worthless however
   much it finds, so the corpus carries 59 clean cases and the certificate denies on one.

## Contributing the useful thing

Send a defect it misses. A ten-line file plus the finding it should have produced is worth more than
a feature request. If you disagree with a finding, send the code that should have been quiet — that
is the other half of the same sentence.

MIT licensed.
