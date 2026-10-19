#!/usr/bin/env python3
"""silentfail.py - find the four defect classes that make a system lie.

WHY THESE FOUR
  They are not invented. Each one was found in a real incident in this estate, and each one has the
  same property: nothing crashes, nothing pages, and the system reports success while doing nothing.

    1 check-cannot-fail        a check whose failure branch still returns success, so the scheduler
                               reads a pass on the night the disk filled.
    2 control-reads-own-text   a scan whose root contains the pattern it scans for, so the alarm is
                               always red and within a week nobody reads it.
    3 record-unread            a record written to a path no reader reads - the ledger that followed
                               the identity of whoever wrote it, so 13 confirmed sends and 0 rows.
    4 test-replaces-subject    a test that substitutes a trivial stand-in for the thing under test,
                               so the exact failure the test exists to catch cannot appear.

  A linter for these is the cheap half of the product: it needs no model, it runs in CI in a second,
  and it fires on real code - it fires on this estate's own tools, which is how it was validated.

DESIGN RULES
  - Every detector must be FALSIFIED in --selftest: the defect is planted, the detector must fire on
    it, the defect is then FIXED in a copy, and the detector must go quiet. A detector that cannot
    go quiet is a false-positive engine and worse than nothing.
  - A detector never raises. An unparseable file is SKIPPED and counted, not fatal, because a check
    that aborts cannot tell you what it saw.
  - Findings name file, line, class, confidence and the evidence that produced them.
  - Exit status is a linter convention: 1 means findings, 0 means clean, 2 means the linter itself
    failed. It never means "I could not decide".

USAGE
  python silentfail.py PATH [PATH ...] [--json] [--min-confidence=low|medium|high]
  python silentfail.py --selftest
"""
import ast
import json
import warnings
import os
import re
import shutil
import sys
import tempfile

CLASSES = ('check-cannot-fail', 'control-reads-own-text', 'record-unread',
           'test-replaces-subject')
HOME = os.path.expanduser(chr(126))
TILDE = chr(126)
DATA_EXT = ('jsonl', 'json', 'log', 'db', 'state', 'txt', 'yaml', 'yml', 'csv')
# A linter people can run on a real repository has to know what a repository looks like: this estate's
# own Documents/AI folder is 37,440 files and 21 GB, almost all of it Flutter and Android build
# output, and an unbounded walk of it did not finish in five minutes.
DEFAULT_EXCLUDES = ('node_modules', '.git', 'build', 'dist', 'venv', '.venv', '__pycache__',
                    '.gradle', '.dart_tool', 'target', 'obj', 'site-packages', '.next', 'out')
MAX_BYTES = 512 * 1024
THRESHOLD = re.compile(r'(limit|max|threshold|cap|pct|usage|percent|free|avail)', re.I)
# A basename ANYWHERE on the line, NOT only a quoted bare filename. The first version required the
# literal to be exactly a filename with no path, so it could not see
# '/home/x/.omni_brain/notify_delivery.jsonl' at all and the record-unread detector was silent on
# the very case it exists for. Slash is built, not typed, for the same reason every other one is.
BASENAME = re.compile(r'([A-Za-z0-9_.-]+\.(?:' + '|'.join(DATA_EXT) + r'))\b')
SLASH = chr(47)
def _is_success(v):
    """Exactly 0 or True, and nothing else.

    NOT False: False == 0 in Python, so a tuple test on (0, True) counted a return of False as
    success and flagged is_within_quota() at high confidence. NOT None either: MEASURED on this
    estate's own anomaly.py, label_of() returns None to mean this line carries no label, which is
    a parser answering a question rather than a check reporting a pass. The class itself is the
    exit-code shape: return 0 whatever happened.
    """
    if v is True:
        return True
    if isinstance(v, int) and not isinstance(v, bool) and v == 0:
        return True
    return False


def finding(cls, path, line, confidence, evidence):
    return {'class': cls, 'file': path, 'line': line, 'confidence': confidence,
            'evidence': evidence}


def _lines(path):
    try:
        with open(path, encoding='utf-8', errors='replace') as fh:
            return fh.read().replace(chr(13) + chr(10), chr(10)).split(chr(10))
    except OSError:
        return []


def _string_spans(path):
    """(line, col) intervals covered by STRING tokens, single-line ones included.

    THE FIRST VERSION SKIPPED ONLY MULTI-LINE STRINGS and therefore still reported
    silentfail.py's own fixture - a one-line string that builds a path with chr(39) concatenation -
    as a writer under HOME. The linter was accusing its own test data, twice in a row, in two
    different ways; that is the argument for string handling done once, properly, with tokenize."""
    import tokenize
    out = set()
    try:
        with open(path, encoding='utf-8', errors='replace') as fh:
            for tok in tokenize.generate_tokens(fh.readline):
                if tok.type != tokenize.STRING:
                    continue
                (sl, sc), (el, ec) = tok.start, tok.end
                if sl == el:
                    out.add((sl, sc, el, ec))
                else:
                    for ln in range(sl, el + 1):
                        out.add((ln, -1, ln, 10 ** 6))
    except (OSError, tokenize.TokenError, SyntaxError, IndentationError):
        return set()
    return out


def _in_string(spans, line, col):
    for (sl, sc, el, ec) in spans:
        if sl <= line <= el:
            if sc <= col <= ec or (sl != el and True):
                return True
    return False


def _string_lines(path):
    """Line numbers that are part of a multi-line string literal in a Python file.

    THE LINTER MUST NOT FLAG THE DATA. reviewer_bench.py embeds the planted sentinel as a string so
    it can plant it, and a grep inside that string is a DESCRIPTION of a defect, not a defect. The
    first run of this file reported exactly that and would have taught users to ignore it."""
    import tokenize
    out = set()
    try:
        with open(path, encoding='utf-8', errors='replace') as fh:
            for tok in tokenize.generate_tokens(fh.readline):
                if tok.type == tokenize.STRING and tok.start[0] != tok.end[0]:
                    out.update(range(tok.start[0], tok.end[0] + 1))
    except (OSError, tokenize.TokenError, SyntaxError, IndentationError):
        return set()
    return out


def _is_test_file(path):
    name = os.path.basename(path).lower()
    parts = [p.lower() for p in path.replace(chr(92), '/').split('/')]
    return (name.startswith('test_') or name.endswith('_test.py') or name.endswith('_test.sh')
            or 'tests' in parts or 'test' in parts)

# ---------------------------------------------------------------- 1. check-cannot-fail

def _returns_success(node):
    """Does this statement block signal SUCCESS on every exit, with no failure signal at all?"""
    saw_return = False
    for stmt in ast.walk(node):
        if isinstance(stmt, ast.Raise):
            return False
        if isinstance(stmt, ast.Return):
            saw_return = True
            val = stmt.value
            # ONLY an explicit success constant counts. A return of a NAME or a CALL is neither a
            # success signal nor a failure signal, and the first version treated it as success, so
            # "if len(s) <= limit: return s" - a correct string-truncating helper - was reported as
            # a check that cannot fail.
            if not (isinstance(val, ast.Constant) and _is_success(val.value)):
                return False
        if isinstance(stmt, ast.Call):
            fn = stmt.func
            name = getattr(fn, 'attr', None) or getattr(fn, 'id', None)
            if name in ('exit', 'sys_exit', '_exit'):
                # sys.exit(0) IS A SUCCESS RETURN AND MUST COUNT AS ONE. Found by cursor reviewing
                # this file: a check written as "if over: print(...); sys.exit(0)" plus a trailing
                # sys.exit(0) never sets saw_return, so the function looked like it had no return at
                # all and the detector stayed silent on a textbook case.
                saw_return = True
                for a in stmt.args:
                    if isinstance(a, ast.Constant) and not _is_success(a.value):
                        return False
    return saw_return


STATUS_TOKENS = re.compile(r'(verify|validate|check|backup|restore|replicate|mirror|integrity)',
                            re.I)
STATUS_READ = r'(?:%s\.returncode|%s\.wait\(\)|%s\.poll\(\))'

def _ignored_status(path):
    """A verification command is run, and its status is never tested.

    WHY THIS IS check-cannot-fail. The appender family on this machine called
    subprocess.run(estate_memory_backup.sh) and subprocess.run([..., '--verify']), printed
    'rc=%d', and returned 0 whatever happened - so the replication the script exists to perform
    could fail completely and the script still said DONE. The script CAN fail (on a missing
    fragment), which is why the branch rule above never saw it; what cannot fail is THIS check.
    Found by auditing this machine's own tooling with agy, 90 findings across 79 files, the same
    two defects in thirteen appenders.
    """
    out = []
    src, tree = _src_tree(path)
    if tree is None:
        return out
    parents = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = getattr(fn, 'attr', None)
        if name not in ('run', 'call'):
            continue
        if any(k.arg == 'check' and isinstance(k.value, ast.Constant) and k.value.value
               for k in node.keywords):
            continue
        # THE COMMAND IS USUALLY A VARIABLE. The first version looked only at list literals in the
        # call and therefore missed the appender it was written for, where the argv arrives from a
        # for-loop over tuples of lists. Resolve a Name through its assignment or its For binding.
        func_node = node
        while func_node is not None and not isinstance(func_node,
                                                      (ast.FunctionDef, ast.AsyncFunctionDef)):
            func_node = parents.get(func_node)

        def strings_of(n):
            return [x.value for x in ast.walk(n)
                    if isinstance(x, ast.Constant) and isinstance(x.value, str)]

        lits = []
        for a in node.args:
            if isinstance(a, (ast.List, ast.Tuple)):
                lits += [e.value for e in a.elts
                         if isinstance(e, ast.Constant) and isinstance(e.value, str)]
            elif isinstance(a, ast.Constant) and isinstance(a.value, str):
                lits.append(a.value)
            elif isinstance(a, ast.Name) and func_node is not None:
                for n in ast.walk(func_node):
                    if isinstance(n, ast.Assign) and any(
                            isinstance(t, ast.Name) and t.id == a.id for t in n.targets):
                        lits += strings_of(n.value)
                    if isinstance(n, ast.For) and isinstance(n.target, ast.Name) \
                            and n.target.id == a.id:
                        lits += strings_of(n.iter)
        if not any(STATUS_TOKENS.search(s) for s in lits):
            continue
        # Is the result used at all? A bare statement keeps nothing.
        parent = parents.get(node)
        target = None
        if isinstance(parent, ast.Assign) and len(parent.targets) == 1 \
                and isinstance(parent.targets[0], ast.Name):
            target = parent.targets[0].id
        # Is it ever tested? returncode comparisons, wait()/poll() results.
        tested = False
        if target:
            tested = bool(re.search(r'\b%s\.returncode\s*(==|!=|>=|<=|>|<|in\b)' % re.escape(target),
                                    src))
        if tested:
            continue
        func = func_node
        returns = [n for n in ast.walk(func) if isinstance(n, ast.Return)] if func else []
        claims_success = any(isinstance(r.value, ast.Constant) and _is_success(r.value.value)
                             for r in returns)
        if not claims_success:
            continue
        out.append(finding('check-cannot-fail', path, node.lineno, 'high',
                           'runs a verification command and never tests its status%s, so a failed '
                           'verification still reports the outcome of the surrounding script'
                           % ('' if target else ' (the result is not even kept)')))
    return out


def _limit_compare(node):
    for sub in ast.walk(node):
        if isinstance(sub, ast.Compare):
            for side in [sub.left] + list(sub.comparators):
                name = getattr(side, 'id', None) or getattr(side, 'attr', None)
                if name and THRESHOLD.search(name):
                    return name
    return None


# ---------------------------------------------------------------- read and parse once

_SRC = {}
_TREES = {}
_SRC_BYTES = {}          # key -> length of the cached source, so the cache is bounded by BYTES
_SRC_TOTAL = [0]         # one mutable counter, so no global statement is needed in _src_tree
# SMALL ON PURPOSE, AND NOT A CACHE OF THE CORPUS. A 48 MB budget (the standard library is 40 MB of
# source) was measured at 890 MB resident and 1,414 MB peak, because an AST is an order of magnitude
# larger than its source: that is the heavy process this tool has no business being. The cache only
# has to survive one file at a time now that every rule reads the tree while the file is open.
CACHE_BYTES = 4 * 1024 * 1024


CHECK_NAME_HINT = re.compile(r'(check|verify|guard|scan|watch|probe|health|valid|assert|probe)',
                             re.I)


def _src_tree(path):
    """Read and parse a Python file ONCE per scan, and return (source, tree).

    WHY THIS EXISTS. Every Python detector opened and parsed the same file, so one scan cost six
    reads and six ast.parse() calls per file. Measured: the CPython standard library (2,417 files)
    took 137 s, and almost all of it was parsing the same bytes over and over. Keyed by path, mtime
    and size so an edit is noticed, bounded so a large tree cannot eat memory, and (None, None) on
    anything unreadable or unparsable - the callers already treat that as nothing to say.
    """
    try:
        st = os.stat(path)
    except OSError:
        return None, None
    key = (path, st.st_mtime_ns, st.st_size)
    if key in _SRC:
        return _SRC[key], _TREES.get(key)
    src = None
    tree = None
    try:
        with open(path, encoding='utf-8', errors='replace') as fh:
            src = fh.read()
        with warnings.catch_warnings():
            # Another program's invalid escape sequence is not this linter's finding, and printing
            # it under our name is how a tool gets a reputation for noise.
            warnings.simplefilter('ignore')
            tree = ast.parse(src)
    except (OSError, SyntaxError, ValueError):
        src = None
        tree = None
    # FIFO BY SOURCE BYTES, NOT CLEAR-ALL ABOVE A FILE COUNT. Measured on the standard library
    # (2,273 files, 40 MB of source): the old rule evicted at 1,200 files, so the cross-file passes
    # began with a cold cache and the scan made 4,365 ast.parse calls for 2,273 files - 2,499 of
    # them re-parsing a file the per-file pass had already parsed. A byte budget holds an ordinary
    # corpus for the length of one scan and degrades to the old behaviour on a tree too large to
    # hold, rather than growing without bound.
    _SRC[key] = src
    _TREES[key] = tree
    _SRC_BYTES[key] = len(src) if src else 0
    _SRC_TOTAL[0] += _SRC_BYTES[key]
    while _SRC_TOTAL[0] > CACHE_BYTES and len(_SRC) > 1:
        oldest = next(iter(_SRC))
        _SRC_TOTAL[0] -= _SRC_BYTES.pop(oldest, 0)
        _SRC.pop(oldest, None)
        _TREES.pop(oldest, None)
    return src, tree


def scan_check_cannot_fail_py(path):
    out = []
    src, tree = _src_tree(path)
    if tree is None:
        return out
    # COMPILED ONCE, NOT PER FILE. re.compile does not cache, and this ran for every Python file in
    # the tree.
    name_hint = CHECK_NAME_HINT
    for func in [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
        # THE RULE IS "a branch that FOUND the problem and returned success", not "a function whose
        # returns all happen to be 0". The first version of this detector said the second thing and
        # produced 61 findings on this estate's own tools, almost all of them guard clauses that
        # skip when there is nothing to do - a false-positive engine of exactly the kind this file
        # exists to complain about.
        returns = [n for n in ast.walk(func) if isinstance(n, ast.Return)]
        cannot_fail = bool(returns) and all(
            isinstance(r.value, ast.Constant) and _is_success(r.value.value)
            for r in returns)
        # THE CHECK IDENTITY, hoisted so the fall-through rule below can use it too: it is
        # carried by the function name OR the file name.
        named_as_check = bool(name_hint.search(func.name)
                              or name_hint.search(os.path.basename(path)))
        for node in [n for n in ast.walk(func) if isinstance(n, ast.If)]:
            limit = _limit_compare(node.test)
            if not limit:
                # A check-like NAME plus a COMPARISON plus a function that cannot fail at all: that
                # triple is what makes the medium rule trustworthy. Name alone produced 363 medium
                # findings on this estate's own folders, which is how a linter earns being ignored.
                # THE FUNCTION IS NOT ALWAYS NAMED LIKE A CHECK. A cron health script is called
                # main(); the FILE is diskcheck.py and its exit status is what cron reads. Found by
                # corpus_cases2: 'def main(): if free < FLOOR: print(...); return 0' with no other
                # return was missed for the whole life of this detector because only func.name was
                # searched. The file name is as much an identity as the function name, and
                # cannot_fail still has to hold, so the rule stays narrow.
                if not (named_as_check and isinstance(node.test, ast.Compare)
                        and cannot_fail):
                    continue
            elif not cannot_fail:
                # THE LIMIT RULE NEEDS cannot_fail TOO. Found by agy reviewing this file: without it,
                # "def is_within_quota(usage, max_limit): if usage <= max_limit: return True;
                # return False" is a HIGH-confidence finding on correct code, because True is a
                # success constant and the branch is only half the function.
                continue
            if not _returns_success(node):
                # A BRANCH WITH NO RETURN STILL SIGNALS NOTHING when the function cannot fail at
                # all: it falls through to the function's own success return. corpus_cases2's
                # space_report writes "if free < FLOOR: print('LOW')" and returns 0 after the
                # if/else, and the branch-local rule reported silence on a textbook cron check.
                # AND A BRANCH THAT RAISES DOES SIGNAL. poetry's scripts/check_argv0.py raises
                # RuntimeError on every failing path and was reported as a silent pass, because
                # the rule only looked for a return; found by running the linter cold on a
                # stranger's repository, which is what the falsifier is for.
                has_return = any(isinstance(n2, (ast.Return, ast.Raise)) for n2 in ast.walk(node))                # AND THE FILE HAS TO BE A CHECK. Without this, view_redacted.py's
                # "if len(lines) > max_lines: print('... N more lines')" - a cosmetic notice in a
                # viewer that returns 0 by design - became a high finding on this estate's own
                # tools the moment the fall-through rule existed. Fall-through proves nothing
                # about a program that is not claiming to decide anything.
                if not (cannot_fail and not has_return and named_as_check):
                    continue
            out.append(finding('check-cannot-fail', path, node.lineno, 'high' if limit else 'medium',
                               'the %s branch of %s() returns success and never signals failure, so '
                               'the caller cannot tell the check from the pass'
                               % (limit or 'failure', func.name)))
    out.extend(_ignored_status(path))
    return _dedupe(out)


def scan_check_cannot_fail_sh(path):
    """The block must be BOUNDED by its own 'fi'. The first version of this detector looked 600
    characters ahead and found the script's trailing 'exit 0', which made it flag the correct
    run_mem_guard.sh - a false positive from reading past the end of the branch, which is the same
    mistake as reading the wrong file."""
    out = []
    lines = _lines(path)
    text = chr(10).join(lines)
    if not text:
        return out
    for m in re.finditer(r'\bif\b[^\n]*\bthen\b', text):
        start = m.start()
        after = text[m.end():]
        # The block ends at the first 'fi' TOKEN, on the same line or not. Requiring a newline
        # before 'fi' meant a one-line "then ...; fi" ran on to the NEXT fi in the file and picked up
        # an exit 0 that belonged to a different branch - catch_caller.sh:6 was reported for the
        # exit 0 that lives on line 9.
        stop = re.search(r'\bfi\b', after)
        block = after[:stop.start()] if stop else after
        tail = after[stop.end():stop.end() + 400] if stop else ''
        body, _sep, rest = block.partition('else') if 'else' in block else (block, '', '')
        # THE CLEAN CASE IS THE ONE WITH exit 0 ON THE SUCCESS PATH. MEASURED on the corpus: a script
        # that exits 0 when the unit is active and exit 3 after the fi is correct, and the first
        # version flagged it because it only looked inside the branch. The defect is a zero where
        # the FAILURE decision is taken - the else branch, or the then branch when nothing after it
        # signals failure either.
        # WHICH BRANCH IS THE FAILURE ONE? Not always the else. A branch that says DOWN, FAILED,
        # ERROR, OVER or CRITICAL and then exits 0 is the defect, wherever it sits; and a branch
        # whose counterpart is empty is the defect too, because nothing else decides the outcome.
        # Found by cursor reviewing this file, which also produced a mirror-shape example it called
        # a false positive: "if active; then exit 0; fi; echo cleanup" really does exit 0 when the
        # unit is down, so the linter was right and the reviewer was wrong about it.
        fail_words = re.compile(r'(down|fail|error|over|critical|missing|absent|denied|timeout|'
                                r'broken|invalid)', re.I)
        zero = re.compile(r'(?:exit|return)\s+0\b')
        nonzero = re.compile(r'(?:exit|return)\s+(?:[1-9]|\$)')
        in_body = bool(zero.search(body))
        in_rest = bool(zero.search(rest)) if rest.strip() else False
        if not (in_body or in_rest):
            continue
        branch = body if in_body else rest
        other = rest if in_body else body
        if nonzero.search(block):
            # This If decides failure somewhere, so it is not a check that cannot fail.
            continue
        # THE SCRIPT'S OWN ABILITY TO FAIL ELSEWHERE. This detector used to look 400 characters
        # past the fi, and _install_import_shadow_cron.sh puts its 'LINES WERE LOST ... exit 1'
        # about 600 characters later: a correct idempotent branch ('if the block is already
        # installed; then exit 0') was reported as a check that cannot fail, in a script that
        # can. The whole rest of the file is the window now, and the label follows the evidence.
        outside = text[:start] + (after[stop.end():] if stop else '')
        script_can_fail = bool(nonzero.search(outside))
        if fail_words.search(branch):
            # The branch SAYS something failed and returns success. Provable only when nothing
            # else in the script can fail; otherwise the caller can tell the run went wrong but
            # not that THIS check failed, which is a maybe and not a finding.
            conf = 'medium' if script_can_fail else 'high'
        elif nonzero.search(other):
            continue
        elif script_can_fail:
            # No failure words anywhere and the script can fail elsewhere: an idempotent skip.
            continue
        else:
            conf = 'high'
        if rest.strip() and re.search(r'exit\s+0\b', body) and not re.search(r'exit\s+[1-9]', rest):
            pass
        # HIGH, not medium. agy's review caught that every shell finding here was 'medium' while
        # main() defaults to a 'high' floor, so the CLI reported 100 percent of nothing for shell
        # scripts - a detector that exists and is unreachable, which is this file's own E-B62.
        out.append(finding('check-cannot-fail', path, text[:start].count(chr(10)) + 1, conf,
                           'the failure branch exits 0: nobody downstream can tell it failed'))
    for line_no, line in enumerate(lines, 1):
        s = line.strip()
        if not (re.search(r'\|\|\s*(?:true|:)(?:\s|$)', s) or re.search(r'2>&1\s*\|\|\s*true', s)):
            continue
        # QUOTE THE CLAUSE THAT IS BEING SWALLOWED. The first version sliced the last 12 characters
        # of the line, so dokku's 'docker rm -f "$C" >/dev/null 2>&1 || true' was reported as
        # 'a failure is swallowed with || ull 2>&1 || true' - evidence a reader cannot act on, and
        # this file's own rule about a control that cannot say what it saw.
        clause = s.split('||')[0].strip()
        out.append(finding('check-cannot-fail', path, line_no, 'medium',
                           'a failing command is swallowed: %s || ...' % clause[-60:]))
    return _dedupe(out)

# ---------------------------------------------------------------- 2. control-reads-own-text

def _expand_shell(pattern, assigns):
    """Substitute $VAR and ${VAR} from this file's own assignments.

    Returns (expanded, resolved). A pattern with no dollar sign is already resolved. A pattern
    whose variable this file does not assign is NOT resolved, and the caller must stay silent:
    guessing is how a correct scanner got reported as matching itself.
    """
    if '$' not in pattern:
        return pattern, True

    def sub(m):
        name = m.group(1)
        if name in assigns:
            return assigns[name].strip().strip(chr(39)).strip(chr(34))
        return m.group(0)

    expanded = re.sub(r'\$\{?([A-Za-z_][A-Za-z0-9_]*)\}?', sub, pattern)
    if '$' in expanded:
        return pattern, False
    return expanded, True


def scan_control_reads_own_text(path):
    out = []
    lines = _lines(path)
    if not lines:
        return out
    text = chr(10).join(lines)
    # Assignment lines, so that a shell variable used as the search root can be resolved:
    # DIR=$(dirname "$0") makes $DIR this script's own directory.
    assigns = {}
    for ln in lines:
        a = re.match(r'\s*([A-Za-z_][A-Za-z0-9_]*)=(.+)$', ln)
        if a:
            assigns[a.group(1)] = a.group(2)
    skip_lines = _string_lines(path) if path.lower().endswith('.py') else set()
    for i, line in enumerate(lines, 1):
        if i in skip_lines or line.lstrip().startswith('#'):
            continue
        # grep, egrep, fgrep, ripgrep and git grep; -R is as recursive as -r; rg and git grep are
        # recursive with no flag at all. Found by agy: the first version matched only a lowercase -r.
        # -r AFTER the path, and "find ... -exec grep" are both real and both were missed. The flag
        # is therefore searched on the whole line rather than in a prefix, and a trailing -exec grep
        # counts as a grep of whatever the find walked.
        m = (re.search(r'\b(grep|egrep|fgrep|rg|git\s+grep)\b'
                       r'((?:\s+-{1,2}[A-Za-z0-9=*.,_/-]+)*)\s+(.*)$', line)
             or re.search(r'\bfind\b.*?-exec\s+(grep|egrep|fgrep)\b((?:\s+-{1,2}'
                          r'[A-Za-z0-9=*.,_/-]+)*)\s+(.*)$', line))
        if not m:
            continue
        tool, flags, rest = m.group(1), m.group(2), m.group(3)
        recursive = (re.search(r'(^|\s)(-[A-Za-z]*[rR]|--recursive)', line)
                     or tool.replace(' ', '') in ('rg', 'gitgrep')
                     or 'find' in line)
        if not recursive:
            continue
        # A scanner that already excludes itself, or that carries --exclude, is doing the right thing.
        if re.search(r'--exclude(-dir)?', flags + ' ' + rest) or re.search(r'-exclude', flags + rest):
            continue
        lit = re.search(r'[\'"]([^\'"]{3,})[\'"]', rest)
        if not lit:
            continue
        pattern = lit.group(1).strip()
        if len(pattern) < 3:
            continue
        # A PATTERN ASSEMBLED FROM A VARIABLE IS NOT THE VARIABLE'S NAME. The estate builds needles
        # as MARKER=PLANTED_SECRET then greps "$MARKER=", so the file never contains the assembled
        # literal - and this detector, comparing the UNEXPANDED '$MARKER=' against the file (which
        # the grep line itself holds), called a correct scanner a self-matcher. Resolve the variable
        # from this file's own assignments first; if it cannot be resolved, stay silent.
        pattern, resolved = _expand_shell(pattern, assigns)
        if not resolved or len(pattern) < 3:
            continue
        root = rest[lit.end():].strip()
        own_root = bool(re.search(r'(dirname|\$0|__file__)', root)) or root in ('.', './')
        var = re.search(r'\$\{?([A-Za-z_][A-Za-z0-9_]*)', root)
        if var and var.group(1) in assigns:
            own_root = own_root or bool(re.search(r'(dirname|\$0|__file__)', assigns[var.group(1)]))
        if not own_root:
            continue
        # THE MATCH IS THE GREP LINE ITSELF, and that is the whole point: the literal only has to
        # appear in the FILE, and a static literal used by grep -r on the script's own directory is
        # in the file by construction. The first version of this detector looked for the literal on
        # ANOTHER line and therefore could never fire on the defect it was written for - a check
        # that could not fail, inside the linter against checks that cannot fail.
        in_file = any(pattern in ln for ln in lines)
        if in_file:
            out.append(finding('control-reads-own-text', path, i, 'high',
                               'recursively greps its OWN directory for %r, a literal this file '
                               'contains, so it always matches itself (needs --exclude or a root '
                               'that does not contain the scanner)' % pattern))
    walk = re.search(r'os\.walk\(|\.rglob\(|\.glob\(|glob\.glob\(|os\.scandir\(', text)
    if walk:
        consts = re.findall(r'^([A-Z_]{3,})\s*=\s*[\'"]([^\'"]{3,})[\'"]', text, re.M)
        for name, value in consts:
            if re.search(r'\b%s\b' % re.escape(name), text[walk.end():]):
                out.append(finding('control-reads-own-text', path, text[:walk.start()].count(chr(10)) + 1,
                                   'low', 'walks a tree while holding %s=%r in this file' % (name, value)))
    return _dedupe(out)

# ---------------------------------------------------------------- 3. record-unread

HOME_WRITER = re.compile(
    r'expanduser\(|Path\.home\(\)|os\.environ\[[\'"]HOME[\'"]\]|'
    r'getenv\([\'"]HOME[\'"]\)|\$\{?HOME\}?|'
    r'[\'"]' + re.escape(TILDE) + r'/')


def _segments(window):
    """The last two path segments in a text window: the directory that should not change, and the
    file that must not move."""
    # The FIRST filename-looking token after the HOME marker, with the segment before it - not the
    # LAST two quoted tokens in the window. Taking the tail of the window picked up {'a': ...} style
    # dictionary keys from the next function and made this detector silently return nothing.
    toks = [(m.start(), m.group(1)) for m in
            re.finditer(r'[\'"]([A-Za-z0-9_.-]+)[\'"]', window)]
    # A token only counts as a FILE if it really has a '.ext', never by suffix alone: 'state' is
    # both a directory name and one of the data extensions, and the suffix test picked the directory
    # as the filename and silently dropped the whole finding.
    for idx, (_pos, tok) in enumerate(toks):
        if BASENAME.fullmatch(tok):
            return (toks[idx - 1][1] if idx > 0 else ''), tok
    parts = [p for p in re.split(r'[\\/]', window) if p and p not in ('.', '..')]
    parts = [p.strip(chr(39)).strip(chr(34)) for p in parts]
    if len(parts) >= 2:
        return parts[-2], parts[-1]
    return '', (parts[-1] if parts else '')


def _home_writers(path):
    out = []
    lines = _lines(path)
    text = chr(10).join(lines)
    spans = _string_spans(path) if path.lower().endswith('.py') else set()
    for m in HOME_WRITER.finditer(text):
        line_no = text[:m.start()].count(chr(10)) + 1
        col = m.start() - (text.rfind(chr(10), 0, m.start()) + 1)
        if _in_string(spans, line_no, col):
            continue
        window = text[m.start():m.start() + 400]
        segs = _segments(window)
        line = text[:m.start()].count(chr(10)) + 1
        if segs[1] and BASENAME.search(segs[1]):
            out.append((line, segs, text[max(0, m.start() - 60):m.start() + 120].replace(chr(10), ' ')))
    return out


# A PATH LITERAL IS NOT A READ. This estate's own estate_notify.py was reported as writing a state
# file nobody reads, and the 'reader' the detector found was the string '/home/x/.omni_brain/
# estate_notify.json' inside a self-test that passes fixture rows to classify(). Requiring an I/O
# verb, or a name bound to the literal that is then read, is the difference between finding the
# defect and accusing every file that mentions a path.
IO_VERB = re.compile(r'\b(open|read_text|read_bytes|readlines|read\(\)|exists|isfile|isdir|stat|glob|'
                     r'rglob|json\.load|load|listdir|scandir|shutil|unlink|rename|copy)\s*\(')
SHELL_IO = re.compile(r'\b(cat|tail|head|grep|egrep|awk|sed|tr|stat|test|ls|find)\b')
# A PLACEHOLDER HOME SEGMENT IS AN EXAMPLE, NOT A DEPLOYMENT: /home/x/user/me/foo paths live in
# self-tests and docstrings, and nothing reads a record there.
PLACEHOLDER = re.compile(r'^([a-z]|user|username|someuser|example|me|nobody|foo|bar|anyone)$')


def _used_as_io(line, literal, text, py):
    """Does this line, or a name bound to this literal, actually READ something?"""
    if IO_VERB.search(line) or (not py and SHELL_IO.search(line)):
        return True
    m = re.search(r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*[\'"]' + re.escape(literal), line)
    if not m:
        return False
    name = m.group(1)
    for m2 in re.finditer(r'\b%s\b' % re.escape(name), text):
        start = text.rfind(chr(10), 0, m2.start()) + 1
        end = text.find(chr(10), m2.end())
        ctx = text[start:end if end > 0 else len(text)]
        if IO_VERB.search(ctx) or (not py and SHELL_IO.search(ctx)):
            return True
    return False


def _absolute_readers(path):
    """A fixed absolute path that something actually READS, as (line, (dir segment, basename)).

    The DIRECTORY SEGMENT IS PART OF THE KEY. Without it, 22 of the 95 findings on this estate's own
    tools were a home-derived writer in one tool matching some unrelated absolute path that merely
    ended in the same filename - noise, and noise is what gets a linter muted."""
    out = []
    # MULTI-LINE STRINGS ONLY for readers: the reader IS a string literal, so span-skipping would
    # hide every reading of a path there is. What has to be skipped is the case where the path is
    # quoted inside a bigger embedded document, which is exactly a multi-line string.
    py = path.lower().endswith('.py')
    spans = _string_lines(path) if py else set()
    lines = _lines(path)
    text = chr(10).join(lines)
    for i, line in enumerate(lines, 1):
        if SLASH not in line or i in spans:
            continue
        for m in re.finditer(r'[\'"](/[^\'"]+)[\'"]', line):
            literal = m.group(1)
            segs = [p for p in literal.split(SLASH) if p]
            if not segs:
                continue
            if len(segs) >= 2 and PLACEHOLDER.match(segs[1].lower()):
                continue
            if not _used_as_io(line, literal, text, py):
                continue
            out.append((i, (segs[-2] if len(segs) >= 2 else '', segs[-1]), line.strip()))
    return out


class _RecordUnread:
    """One file's contribution, added while the file is open, then compared across the scan.

    WHY A COLLECTOR AND NOT A SECOND PASS. The three cross-file rules used to iterate every source
    file again after the per-file pass had already parsed it, and each began with a cache filled by
    a different set of files: measured on the CPython standard library, 2,499 of 4,365 ast.parse
    calls were re-parsing a file the scan had already opened. Adding one file's facts at the moment
    it is open costs nothing and leaves the comparison identical.
    """

    def __init__(self):
        self.writers = []
        self.readers = []
        self.unit_lines = []

    def add(self, path):
        """One file's contribution.

        A TEST IS NOT A PRODUCTION PEER. test_oom_delta.py reads
        /home/svc/.omni_brain/swap_headroom.state.json ON PURPOSE to verify the deployed file, and
        the first version of this detector reported the watcher as writing a record nobody reads - a
        false positive on two production files caused by a test harness doing exactly what it should.
        The asymmetry that matters is between the code that runs and the code that reads, not between
        the code that runs and the code that checks it.
        """
        if path.lower().endswith(('.service', '.timer')):
            self.unit_lines += _lines(path)
        if _is_test_file(path):
            return
        for line, name, ev in _home_writers(path):
            self.writers.append((path, line, name, ev))
        if path.endswith('.py') or path.endswith('.sh'):
            for line, name, ev in _absolute_readers(path):
                self.readers.append((path, line, name, ev))

    def decide(self):
        out = []
        for wpath, wline, wsegs, wev in self.writers:
            for rpath, rline, rsegs, rev in self.readers:
                if rpath == wpath and abs(rline - wline) < 3:
                    continue
                wname = wsegs[1]
                rname = rsegs[1]
                if wname == rname and wsegs[0] == rsegs[0]:
                    # HIGH only when the identity is decided SOMEWHERE ELSE - a systemd unit in the
                    # same tree that names a User. Otherwise the two ways of expressing one path still
                    # resolve to the same file for one person: a maintenance hazard, not a live loss.
                    conf = 'high' if any('User=' in ln for ln in self.unit_lines) else 'medium'
                    out.append(finding('record-unread', wpath, wline, conf,
                                       'writes %s/%s under HOME while %s:%d reads the same '
                                       'directory and file by absolute path - under a different '
                                       'identity the row lands where nobody reads'
                                       % (wsegs[0], wname, os.path.basename(rpath), rline)))
        return _dedupe(out)


def scan_record_unread(files):
    """Cross-file: a writer whose path follows HOME, and a reader that reads a fixed absolute path
    with the same basename. Two files that never agree, and nothing that would ever say so."""
    col = _RecordUnread()
    for path in files:
        col.add(path)
    return col.decide()

# ---------------------------------------------------------------- 4. test-replaces-subject

# The separator had to allow "] = " - os.environ['K'] = 'v' is the most common form and the
# first version of this pattern silently skipped every one of them.
ENV_SET = re.compile(
    r'(?:os\.environ\[|os\.environ\.setdefault\(|monkeypatch\.setenv\(|environ\.put\(|'
    r'export\s+)([\'"])?([A-Z][A-Z0-9_]{2,})\1?\s*(?:\]\s*[=:]|=(?!=)|,)\s*'
    r'([\'"][^\'"]*[\'"]|[A-Za-z0-9_.:/-]+)')

# A TEST THAT REBINDS THE SUBJECT TO A MOCK. The first version of this detector only understood
# environment overrides, so 'sender.deliver = mock.Mock(...)' followed by
# 'sender.deliver.assert_called_once_with(...)' - a test that measures its own stand-in - was
# invisible. Found by corpus_cases2/mock_self_assert.
REBIND_ASSIGN = re.compile(
    r'^[ \t]*([A-Za-z_][A-Za-z0-9_]*)\s*\.\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*'
    r'(?:(?:mock|unittest\.mock)\.)?(?:Magic|Async|NonCallable)?Mock\s*\(',
    re.M)
REBIND_SETATTR = re.compile(
    r'(?:monkeypatch\.setattr|mock\.patch\.object)\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*,\s*'
    r'[\'"]([A-Za-z_][A-Za-z0-9_]*)[\'"]\s*,\s*'
    r'(?:(?:mock|unittest\.mock)\.)?(?:Magic|NonCallable)?(?:Mock|lambda)')


# A SUBJECT THAT READS A NAME IS THE OTHER HALF OF THE DEFECT, not merely the same file. One pass
# over the text instead of one regex per subject.
ENV_READ = re.compile(r'(?:os\.environ\.get\(|os\.getenv\(|os\.environ\[)'
                      r'[\'"]([A-Z][A-Z0-9_]{2,})[\'"]')


class _TestReplaces:
    """Which tests configure or replace a subject, decided after every file has been seen."""

    def __init__(self):
        self.tests = []
        self.reads = {}
        self.mods = {}

    def add(self, path):
        if _is_test_file(path):
            self.tests.append(path)
            return
        text = chr(10).join(_lines(path))
        for m in ENV_READ.finditer(text):
            line = text[:m.start()].count(chr(10)) + 1
            self.reads.setdefault(m.group(1), []).append((path, line))
        # ---- a test that REBINDS the subject's own function to a Mock and then asserts on the Mock.
        # The subject is identified by module stem, and the target has to be a function the subject
        # module actually defines at top level, so patching an external dependency stays clean.
        if not path.endswith('.py'):
            return
        _text, tree = _src_tree(path)
        if tree is None:
            return
        funcs = {}
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                funcs[node.name] = node.lineno
        if funcs:
            self.mods[os.path.splitext(os.path.basename(path))[0]] = (path, funcs)

    def decide(self):
        out = []
        for path in self.tests:
            text = chr(10).join(_lines(path))
            for m in ENV_SET.finditer(text):
                key = m.group(2)
                if key not in self.reads:
                    continue
                # A TEST THAT CONFIGURES A VALUE IS NOT A TEST THAT REPLACES THE SUBJECT. Found by
                # agy: monkeypatch.setenv('HTTP_TIMEOUT', '1') was reported as standing in for the
                # code under test. The defect is replacing the EXECUTABLE, so either the value looks
                # like a stand-in (true, echo, a colon) or the subject hands that variable to a shell.
                value = (m.group(3) or '').strip().strip(chr(39)).strip(chr(34))
                stand_in = value.lower() in ('true', 'false', 'echo', '/bin/true', '/usr/bin/true',
                                             ':', 'cat', 'noop', 'no-op', 'sleep 0')
                # NEAR the shell call, not merely in the same file. Found by cursor: "subprocess" in
                # the module for an unrelated reason made every env override in its tests a high
                # finding. Proximity is the cheapest honest proxy for relatedness.
                subject_text = chr(10).join(_lines(self.reads[key][0][0]))
                piped = False
                for m2 in re.finditer(r'(subprocess|os\.system|popen|shell\s*=\s*True)', subject_text):
                    window = subject_text[max(0, m2.start() - 300):m2.start() + 300]
                    if key in window:
                        piped = True
                        break
                if not (stand_in or piped):
                    continue
                line = text[:m.start()].count(chr(10)) + 1
                where = self.reads[key][0]
                out.append(finding('test-replaces-subject', path, line, 'high',
                                   'the test overrides %s and asserts on the stand-in, while %s:%d '
                                   'reads %s in production'
                                   % (key, os.path.basename(where[0]), where[1], key)))
            hits = [(m.group(1), m.group(2), m.start()) for m in REBIND_ASSIGN.finditer(text)]
            hits += [(m.group(1), m.group(2), m.start()) for m in REBIND_SETATTR.finditer(text)]
            for mod, attr, pos in hits:
                if mod not in self.mods:
                    continue
                subj_path, funcs = self.mods[mod]
                if attr not in funcs:
                    continue
                # A PRIVATE HELPER IS A SEAM, NOT THE SUBJECT. mem_guard's test replaces the private
                # _meminfo that reads /proc and then asserts on the real check() - the legitimate
                # dependency stub the clean controls exist for - and the first version of this rule
                # called it a replacement of the subject. Only a PUBLIC function stands in for the
                # thing under test.
                if attr.startswith('_'):
                    continue
                asserts = re.search(r'\b%s\s*\.\s*%s\s*\.\s*assert'
                                    % (re.escape(mod), re.escape(attr)), text)
                out.append(finding(
                    'test-replaces-subject', path, text[:pos].count(chr(10)) + 1,
                    # WITHOUT an assertion on the Mock itself nothing proves the test measures the
                    # stand-in, so the replacement is a maybe and not a finding.
                    'high' if asserts else 'low',
                    'the test rebinds %s.%s to a Mock%s, so the assertion measures the stand-in '
                    'rather than %s:%d' % (mod, attr,
                                           ' and then asserts on that Mock' if asserts else '',
                                           os.path.basename(subj_path), funcs[attr])))
        return _dedupe(out)


def scan_test_replaces_subject(files):
    col = _TestReplaces()
    for path in files:
        col.add(path)
    return col.decide()

# ---------------------------------------------------------------- driver

def _dedupe(findings):
    seen = set()
    out = []
    for f in findings:
        key = (f['class'], f['file'], f['line'])
        if key in seen:
            continue
        seen.add(key)
        out.append(f)
    return out


# ---------------------------------------------------------------- 5. dead guard on a normalised value

def _const_str(node):
    """The string a normalising expression is built from.

    chr(13) + chr(10) is NOT an ast.Constant, and requiring one is how a rule silently misses the
    only shape this estate writes: read_norm() builds its patterns from chr(N) precisely to keep a
    carriage return out of its own source.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        a, b = _const_str(node.left), _const_str(node.right)
        return None if a is None or b is None else a + b
    if isinstance(node, ast.Call) and getattr(node.func, 'id', None) == 'chr' and len(node.args) == 1:
        arg = node.args[0]
        if isinstance(arg, ast.Constant) and isinstance(arg.value, int):
            return chr(arg.value)
    return None


def _unescape(pattern):
    return pattern.replace('\\r', chr(13)).replace('\\n', chr(10)).replace('\\t', chr(9))


def _removed_chars(node):
    """Characters this expression REMOVES: replace(A, B) where B omits part of A, and re.sub(A, B)."""
    removed = set()
    for call in ast.walk(node):
        if not isinstance(call, ast.Call):
            continue
        name = getattr(call.func, 'attr', None)
        if name in ('replace', 'sub') and len(call.args) >= 2:
            a, b = _const_str(call.args[0]), _const_str(call.args[1])
            if not a or b is None:
                continue
            if name == 'sub' and len(a) > 3:
                continue
            a = _unescape(a)
            # A DOUBLED PATTERN REMOVES PAIRS, NOT THE CHARACTER. configparser.py strips escaped
            # percents with value.replace('%%', '') and then asks 'if "%" in tmp_value', which can
            # absolutely fire because a bare percent survives. The rule read that as 'removed %'
            # and called three healthy standard-library guards dead. Found by the falsifier.
            if len(set(a)) == 1 and len(a) > 1:
                continue
            removed |= set(a) - set(b)
    return removed


# A GUARD THAT TESTS FOR SOMETHING THE VALUE CAN NO LONGER CONTAIN is a dataflow question, not a
# syntactic one, which is why this detector did not exist until a reviewer found thirty-six
# instances of it in this repository's own appenders (E-B211): read_norm() replaces CRLF and CR with
# LF, and every caller then asked 'if chr(13) in body'. The check has never been able to fire. This
# rule answers exactly that question and no more: which characters were removed on the way here, and
# does the guard test for one of them.
def _scope_chain(node, parents, scope_of):
    """The module scope plus every function that encloses this node, innermost last.

    THE SEMANTICS ARE DELIBERATELY UNCHANGED FROM THE ORIGINAL ast.walk-PER-SCOPE VERSION: a node
    inside a nested function belongs to the outer scope too, because an outer assignment is still
    the value a nested guard reads, and that is what the corpus certifies.
    """
    chain = []
    cur = node
    while cur in parents:
        cur = parents[cur]
        idx = scope_of.get(id(cur))
        if idx is not None:
            chain.append(idx)
    # MODULE FIRST, EACH SCOPE ONCE. Walking to the root reaches the module node too, so appending
    # it there as well left every chain with a duplicate module entry - harmless for the taint
    # lookup, but it hid the nested-scope mistake from the fixture that exists to catch it.
    return tuple(reversed(chain))


class _DeadGuard:
    """Normalisation and guard facts, collected while each file is open, decided once at the end.

    THE DECISION NEEDS THE WHOLE SCAN, THE PARSING DOES NOT. Which characters a helper removes is
    only known after every file has been seen, which is why this rule used to keep every parse tree
    alive and walk them again: measured on the CPython standard library, 1,841 redundant ast.parse
    calls and the whole corpus resident at once. The facts below are small enough to keep instead.
    """

    def __init__(self):
        self.removers = {}
        self.facts = []

    def add(self, path):
        if not path.lower().endswith('.py'):
            return
        _text, tree = _src_tree(path)
        if tree is None:
            return
        parents = {}
        scopes = [tree]
        scope_of = {id(tree): 0}
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                parents[child] = node
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                scope_of[id(node)] = len(scopes)
                scopes.append(node)
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                chars = _removed_chars(node)
                if chars:
                    self.removers.setdefault(node.name, set()).update(chars)
        assigns = []
        compares = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
                    continue
                chars = _removed_chars(node.value)
                fname = None
                if isinstance(node.value, ast.Call):
                    fname = (getattr(node.value.func, 'id', None)
                             or getattr(node.value.func, 'attr', None))
                if not chars and not fname:
                    continue
                assigns.append((_scope_chain(node, parents, scope_of), node.lineno,
                                node.targets[0].id, frozenset(chars), fname))
            elif isinstance(node, ast.Compare):
                if not any(isinstance(op, ast.In) for op in node.ops):
                    continue
                left = _const_str(node.left)
                if not left:
                    continue
                names = tuple(c.id for c in node.comparators if isinstance(c, ast.Name))
                if not names:
                    continue
                compares.append((_scope_chain(node, parents, scope_of), node.lineno, left, names))
        if assigns or compares:
            self.facts.append((path, assigns, compares))

    def decide(self):
        out = []
        for path, assigns, compares in self.facts:
            if not assigns:
                continue
            taint = {}
            for chain, lineno, name, chars, fname in sorted(assigns, key=lambda a: a[1]):
                ch = chars
                if fname in self.removers:
                    ch = ch | self.removers[fname]
                if not ch:
                    continue
                for sidx in chain:
                    scope_taint = taint.setdefault(sidx, {})
                    prev = scope_taint.get(name)
                    scope_taint[name] = (lineno, ch if prev is None else (prev[1] | ch))
            if not taint:
                continue
            for chain, lineno, left, names in compares:
                for sidx in chain:
                    scope_taint = taint.get(sidx)
                    if not scope_taint:
                        continue
                    for name in names:
                        hit = scope_taint.get(name)
                        if hit is None or hit[0] >= lineno:
                            continue
                        if set(left) & hit[1]:
                            out.append(finding('check-cannot-fail', path, lineno, 'high',
                                               'tests for %r in %s after %s was normalised to '
                                               'remove it, so the guard can never fire'
                                               % (left[:12], name, name)))
        return _dedupe(out)


def scan_dead_guard(files):
    col = _DeadGuard()
    for path in files:
        col.add(path)
    return col.decide()


# ---------------------------------------------------------------- 6. constant nothing reads

def _looks_like_path(value):
    """A string that addresses a file: absolute, home-anchored, or carrying a known extension."""
    v = (value or '').strip()
    if not v or '://' in v:
        return False
    if v.startswith('/') or v.startswith('./') or v.startswith('~/'):
        return True
    if re.match(r'^[A-Za-z]:[\\/]', v):
        return True
    return bool(re.search(r'\.(md|txt|json|jsonl|csv|tsv|log|yaml|yml|toml|sh|py|conf|ini|cfg|db|sqlite|sqlite3|gz|xz|zip|xml|html|lock|state)$', v))


def scan_unread_constant(path):
    """A module-level constant that no line of this file ever reads.

    MEASURED, same audit: _append_memory22.py declares FH = '/tmp/_append_history22.md' and never
    appends to it while backing up SYSTEM_HISTORY.md - the fragment is written and then lost. The
    rule is deliberately narrow: an ALL-CAPS string constant in a SCRIPT (it has a __main__ guard, so
    it is not a library exporting names to importers) whose name occurs exactly once in the file.
    """
    out = []
    if not path.lower().endswith('.py'):
        return out
    src, tree = _src_tree(path)
    if tree is None:
        return out
    if '__name__' not in src or '__main__' not in src:
        return out
    # COUNT IDENTIFIERS ONCE. The first version ran re.findall(r'\bNAME\b', src) for every
    # constant, which re-scanned the whole file per declaration; the standard library spent 31 s in
    # this rule alone. One token pass answers every lookup the same way, word boundary and all.
    tokens = {}
    for tok in re.findall(r'[A-Za-z_][A-Za-z0-9_]*', src):
        tokens[tok] = tokens.get(tok, 0) + 1
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        # TUPLE UNPACKING COUNTS. The first version required one Name target and missed
        # "FE, FH = '/tmp/a.md', '/tmp/b.md'" - the exact declaration in the file this rule was
        # written for, where FE is used and FH is not.
        pairs = []
        target = node.targets[0]
        if isinstance(target, ast.Name):
            pairs.append((target.id, _const_str(node.value)))
        elif isinstance(target, ast.Tuple) and isinstance(node.value, (ast.Tuple, ast.List)):
            values = node.value.elts
            if len(values) == len(target.elts):
                for t, v in zip(target.elts, values):
                    if isinstance(t, ast.Name):
                        pairs.append((t.id, _const_str(v)))
        for name, value in pairs:
            if value is None or not re.fullmatch(r'[A-Z][A-Z0-9_]{1,}', name):
                continue
            # AND THE VALUE HAS TO BE A RECORD'S ADDRESS. The rule's premise is a path written and
            # never read back; a constant holding 'abort' or 'legacy C-API' is an exported value,
            # and eleven standard-library modules were accused because their demo blocks satisfy
            # the __main__ test. Found by the falsifier.
            if not _looks_like_path(value):
                continue
            if tokens.get(name, 0) == 1:
                out.append(finding('record-unread', path, node.lineno, 'high',
                                   'declares %s and no line of this file reads it' % name))
    return out


# ---------------------------------------------------------------- 7. a check that is only printed

# THE SCRIPT HAS TO BE CLAIMING AN OUTCOME for this rule to mean anything: printing a diagnostic in a
# viewer is the viewer's job. So the file, or the directory it sits in, has to say what it is for.
CHECKISH = re.compile(r'(check|verify|guard|append|audit|validate|sync|gate|memory|probe|watch|'
                      r'health|sentinel)', re.I)
PREDICATE = re.compile(r'(endswith|startswith|is_file|is_dir|exists|issubset|isdisjoint|isalnum|'
                       r'isdigit)$')


def scan_printed_check(path):
    """A check whose result is printed and never decided on.

    MEASURED, same audit (E-B211): fourteen appenders compute the thing they exist to verify -
    duplicate headings, a marker still at the head of its own entry, a file that is still not
    newline-terminated - print it, and return 0. The reader sees a line of prose; the exit status
    says success. Two shapes, both here: a boolean test inside print(), and a value whose every use
    in the file is a print argument.
    """
    out = []
    if not path.lower().endswith('.py') or _is_test_file(path):
        return out
    if not (CHECKISH.search(os.path.basename(path))
            or CHECKISH.search(os.path.basename(os.path.dirname(path)))):
        return out
    _text, tree = _src_tree(path)
    if tree is None:
        return out
    parents = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node

    def inside_print(node):
        cur = parents.get(node)
        while cur is not None:
            if isinstance(cur, ast.Call) and getattr(cur.func, 'id', None) == 'print':
                return True
            cur = parents.get(cur)
        return False

    # THE FIRST VERSION OF THIS RULE REPORTED 192 FINDINGS IN THIS REPOSITORY, nearly all of them a
    # report tool printing a statistic - which is the report tool doing its job. Two constraints cut
    # it to the defect: the value being printed must be tested NOWHERE else in the file, and the
    # function doing the printing must be one that claims an outcome (it returns a success constant
    # or exits 0). A reporter returns None and is not making a claim. The "name only ever printed"
    # shape was dropped entirely: it cannot tell a check from a counter.
    tested_names = set()
    for node in ast.walk(tree):
        tests = []
        if isinstance(node, ast.If) or isinstance(node, ast.While):
            tests.append(node.test)
        elif isinstance(node, ast.Assert):
            tests.append(node.test)
        elif isinstance(node, ast.Return) and node.value is not None:
            tests.append(node.value)
        # A BoolOp IS ONLY A TEST WHEN IT IS ONE. Treating every BoolOp in the file as a test put
        # `dup` into tested_names because it appeared inside `print(dup or 'none')`, and the narrow
        # shape-2 rule then reported nothing - the fifth time a rule in this file has been unable to
        # fire on the case it was written for.
        for test in tests:
            for sub in ast.walk(test):
                if isinstance(sub, ast.Name):
                    tested_names.add(sub.id)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or getattr(node.func, 'id', None) != 'print':
            continue
        func = parents.get(node)
        while func is not None and not isinstance(func, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func = parents.get(func)
        if func is None:
            continue
        claims = any(isinstance(r, ast.Return) and isinstance(r.value, ast.Constant)
                     and _is_success(r.value.value)
                     for r in ast.walk(func))
        if not claims:
            continue
        def inside_comprehension(sub):
            # A COMPARISON INSIDE A COMPREHENSION IS AN ELEMENT SELECTOR, NOT A CHECK.
            # audit_repo.py:336 prints len([1 for _p, w in dropped if w == why]) - a count of
            # matches - and the first version of this rule called it a check whose result cannot
            # change the exit status.
            cur = parents.get(sub)
            while cur is not None and cur is not node:
                if isinstance(cur, (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp)):
                    return True
                cur = parents.get(cur)
            return False

        for sub in ast.walk(node):
            names = set()
            label = None
            if inside_comprehension(sub):
                continue
            if isinstance(sub, ast.Compare):
                names = {n.id for n in ast.walk(sub) if isinstance(n, ast.Name)}
                label = 'the result of a comparison'
            elif isinstance(sub, ast.Call) and PREDICATE.search(getattr(sub.func, 'attr', '') or ''):
                names = {n.id for n in ast.walk(sub) if isinstance(n, ast.Name)}
                label = 'a %s() result' % sub.func.attr
            if not label or not names or (names & tested_names):
                continue
            out.append(finding('check-cannot-fail', path, node.lineno, 'high',
                               'prints %s and decides on it nowhere in this file, while the '
                               'function returns success' % label))
            break
    # SHAPE 2, NARROWLY: a value whose name says it is a finding (dup, missing, mismatch ...) and
    # whose every use is a print. Medium, not high: the name is evidence about intent, not proof, and
    # the default floor should not carry a maybe. The broad version of this shape - any value used
    # only in prints - reported 192 findings in this repository and could not tell a check from a
    # counter, which is how a linter earns being ignored.
    FINDING_NAME = re.compile(r'(dup|duplicate|missing|mismatch|stale|invalid|orphan|conflict|'
                              r'violation|extra|unexpected)', re.I)
    assigned = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            assigned[node.targets[0].id] = node.lineno
    loads = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            loads.setdefault(node.id, []).append(inside_print(node))
    for name, line in assigned.items():
        uses = loads.get(name) or []
        if not uses or not all(uses) or name in tested_names:
            continue
        if not FINDING_NAME.search(name):
            continue
        out.append(finding('check-cannot-fail', path, line, 'medium',
                           'computes %s, every use of it is a print, and the name says it is a '
                           'finding: nothing it reports can change the exit status' % name))
    return _dedupe(out)


# ---------------------------------------------------------------- 8. a pipeline that cannot fail

PIPE_TESTS = ('grep', 'egrep', 'fgrep', 'rg')
PIPE_TRANSFORMERS = ('sort', 'tail', 'head', 'uniq', 'wc')


def scan_masked_pipeline(path):
    """A test piped through a command that always succeeds, in a set -e script with no pipefail.

    MEASURED, same audit: thirteen shell appenders end with a grep of the error headings piped into
    tail, under set -e and no pipefail. The pipeline status is tail status, which is 0, so the
    script failure model - abort on error - cannot see that the grep found nothing or that the file
    was unreadable. Medium, not high: without intent a display pipeline and a check look identical,
    and the evidence says exactly that rather than pretending to know.
    """
    out = []
    if not path.lower().endswith(('.sh', '.bash')):
        return out
    try:
        with open(path, encoding='utf-8', errors='replace') as fh:
            text = fh.read()
    except OSError:
        return out
    if not re.search(r'^\s*set\s+-[a-zA-Z]*e', text, re.M):
        return out
    if 'pipefail' in text:
        return out
    for i, line in enumerate(text.split(chr(10)), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith('#') or '|' not in line:
            continue
        stages = [s.strip() for s in line.split('|') if s.strip()]
        if len(stages) < 2:
            continue
        first = stages[0].split()[0].split('/')[-1]
        last = stages[-1].split()[0].split('/')[-1]
        if first not in PIPE_TESTS or last not in PIPE_TRANSFORMERS:
            continue
        # HIGH WHEN THE SCRIPT'S OWN NAME SAYS IT IS A CHECK. The masking is a POSIX fact; the only
        # uncertainty is whether the pipeline was meant as a test, and a file called check_headings.sh
        # has already answered that. A display pipeline in a script that does not claim to check
        # anything stays medium, where maybes belong.
        conf = 'high' if CHECKISH.search(os.path.basename(path)) else 'medium'
        out.append(finding('check-cannot-fail', path, i, conf,
                           'a %s piped into %s: the status is the %s status, so a failed %s cannot '
                           'abort this set -e script (no pipefail)' % (first, last, last, first)))
    return _dedupe(out)


def scan(paths, excludes=None, max_bytes=None, walk_all=False):
    """Group by directory so the cross-file detectors can see writer and reader together."""
    excludes = tuple(excludes if excludes is not None else DEFAULT_EXCLUDES)
    max_bytes = MAX_BYTES if max_bytes is None else max_bytes
    findings, skipped, walked = [], 0, 0
    # SOURCE FILES ONLY for the cross-file detectors. A markdown note that quotes a ledger path is
    # not a writer, and this estate has 60 of them. .service files travel WITH the sources: they are
    # where the identity is decided, and without them a real identity-changing unit and a harmless
    # duplicate path grade the same.
    _ru, _tr, _dg = _RecordUnread(), _TestReplaces(), _DeadGuard()
    files_by_dir = {}
    for root in paths:
        if os.path.isfile(root):
            files_by_dir.setdefault(os.path.dirname(os.path.abspath(root)), []).append(root)
            continue
        for dirpath, dirs, names in os.walk(root):
            if not walk_all:
                dirs[:] = [d for d in dirs if d.lower() not in excludes]
            for name in names:
                full = os.path.join(dirpath, name)
                try:
                    if max_bytes and os.path.getsize(full) > max_bytes:
                        skipped += 1
                        continue
                except OSError:
                    skipped += 1
                    continue
                walked += 1
                files_by_dir.setdefault(os.path.abspath(dirpath), []).append(full)
    for _d, files in sorted(files_by_dir.items()):
        for path in files:
            low = path.lower()
            if low.endswith('.py'):
                if not low.endswith('_test.py') and not os.path.basename(low).startswith('test_'):
                    findings += scan_check_cannot_fail_py(path)
                else:
                    findings += scan_check_cannot_fail_py(path)
                findings += scan_control_reads_own_text(path)
                findings += scan_unread_constant(path)
                findings += scan_printed_check(path)
            elif low.endswith(('.sh', '.bash')):
                findings += scan_check_cannot_fail_sh(path)
                findings += scan_control_reads_own_text(path)
                findings += scan_masked_pipeline(path)
            elif not low.endswith('.service'):
                skipped += 1
            # THE SAME FILE, STILL OPEN, ONE PARSE. These three rules answer CROSS-FILE questions and
            # therefore decide only after every file has been seen - but they no longer re-open every
            # file to do it. Measured on the standard library: 4,365 ast.parse calls for 2,273 files
            # before, 1,866 after, with the findings byte-identical on nine corpora.
            if low.endswith(('.py', '.sh', '.bash', '.service')):
                _ru.add(path)
                _tr.add(path)
                _dg.add(path)
    # ACROSS THE WHOLE SCAN, NOT PER DIRECTORY. Found by agy reviewing this file: grouping by the
    # immediate parent meant a writer in daemon/ and a reader in systemd/ were never compared, and a
    # tests/ subdirectory holds no non-test subjects at all, so test-replaces-subject was blind in
    # exactly the layout every real repository uses.
    findings += _ru.decide()
    findings += _tr.decide()
    findings += _dg.decide()
    return _dedupe(findings), skipped, walked


def report(findings, paths):
    if not findings:
        return 'silentfail: no findings in %s' % ', '.join(paths)
    lines = ['silentfail: %d finding(s)' % len(findings)]
    for f in sorted(findings, key=lambda x: (x['class'], x['file'], x['line'])):
        lines.append('%s:%d: [%s] %s (%s)' % (f['file'], f['line'], f['class'],
                                              f['evidence'], f['confidence']))
    return chr(10).join(lines)

# ---------------------------------------------------------------- selftest

def _corpus():
    return os.path.join(HOME, '.dsh_bench', 'cases')


def _ship_corpus(dest=None):
    """Plant the corpus that SHIPS beside this module, and return the directory.

    The selftest was written where the corpus lived in a bench directory outside the tool, and it
    refused to run without it. A public tool cannot refuse its own selftest on a machine that only
    pip-installed it, and it must not skip the checks either: a skipped check is the same silent
    pass this linter exists to find. So the corpus travels with the module and is planted into a
    throwaway directory when the bench copy is absent.
    """
    try:
        import corpus_data
        data = {'cases': corpus_data.CASES}
    except Exception:
        src = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'corpus.json')
        if not os.path.isfile(src):
            return None
        with open(src, encoding='utf-8') as fh:
            data = json.load(fh)
    dest = dest or tempfile.mkdtemp(prefix='silentfail_ship_')
    for case, files in (data.get('cases') or {}).items():
        for name, body in files.items():
            p = os.path.join(dest, case, name)
            parent = os.path.dirname(p)
            if parent:
                os.makedirs(parent, exist_ok=True)
            with open(p, 'w', encoding='utf-8', newline=chr(10)) as fh:
                fh.write(body)
    return dest


def selftest():
    ok = fail = 0
    notes = []

    def check(name, cond, detail=''):
        nonlocal ok, fail
        if cond:
            ok += 1
        else:
            fail += 1
            notes.append('FAIL %s -> %s' % (name, detail))

    cases = _corpus()
    planted = None
    if not os.path.isdir(cases):
        planted = _ship_corpus()
        cases = planted or cases
    truth = {
        'disk_guard': ('check-cannot-fail', 'check_disk.py'),
        'leak_sentinel': ('control-reads-own-text', 'sentinel.sh'),
        'notify_path': ('record-unread', 'notify.py'),
        'notify_test': ('test-replaces-subject', 'test_notify.py'),
    }
    if not os.path.isdir(cases):
        print('REFUSING: the planted corpus is not present at %s; run reviewer_bench.py '
              '--plant first' % cases)
        return 2
    # THE FIRES CHECKS ARE SCOPED TO THEIR BASE DIRECTORY. The planted tree also holds
    # disk_guard_ren and disk_guard_svc, which contain the same defective file by design, so a
    # whole-tree scan counts three hits and the check read as a detector failure. The clean
    # control below still scans the WHOLE tree, because a detector that only survives the top
    # level is not a detector.
    findings, skipped, walked = scan([os.path.join(cases, c) for c in truth])
    by_class = {}
    for f in findings:
        by_class.setdefault(f['class'], []).append(f)
    for case, (cls, fname) in truth.items():
        hits = [f for f in findings if f['class'] == cls and os.path.basename(f['file']) == fname]
        check('fires-%s' % cls, len(hits) == 1, [(os.path.basename(x['file']), x['line']) for x in hits])
        check('case-%s-is-true' % case, bool(hits) and case in [os.path.basename(os.path.dirname(h['file'])) for h in hits],
              [h['file'] for h in hits])
    every_finding, _sk_all, _wk_all = scan([cases])
    clean = [f for f in every_finding if 'mem_guard' in f['file']]
    check('clean-control-silent', clean == [], clean)

    # FALSIFY each detector: fix the defect in a copy, the detector must go quiet.
    tmp = tempfile.mkdtemp(prefix='silentfail_falsify_')
    try:
        for case in truth:
            src = os.path.join(cases, case)
            dst = os.path.join(tmp, case)
            shutil.copytree(src, dst)
        fix_defect = {
            'disk_guard': ('check_disk.py',
                           "        print('DISK-OVER-LIMIT",
                           "        print('DISK-OVER-LIMIT"),
            'leak_sentinel': ('sentinel.sh', '"$DIR"', '/srv/config'),
            'notify_path': ('notify.py', 'expanduser(chr(126))', "'/home/svc'"),
            'notify_test': ('test_notify.py', "os.environ['ESTATE_NOTIFY_CMD'] = 'true'", ''),
        }
        fixed_ok = True
        p = os.path.join(tmp, 'disk_guard', 'check_disk.py')
        body = open(p, encoding='utf-8').read()
        fixed = body.replace('return 0' + chr(10) + "    print('disk ok", 'return 3' + chr(10) + "    print('disk ok")
        if fixed == body:
            fixed_ok = False
        open(p, 'w', encoding='utf-8', newline=chr(10)).write(fixed)
        check('falsify-disk-fix-applied', fixed_ok)
        for case, (fname, old, new) in fix_defect.items():
            if case == 'disk_guard':
                continue
            p = os.path.join(tmp, case, fname)
            body = open(p, encoding='utf-8').read()
            if old not in body:
                check('falsify-%s-site-found' % case, False, old)
                continue
            open(p, 'w', encoding='utf-8', newline=chr(10)).write(body.replace(old, new))
        fixed_findings, _sk, _wk = scan([tmp])
        for case, (cls, fname) in truth.items():
            left = [f for f in fixed_findings if f['class'] == cls and fname == os.path.basename(f['file'])]
            check('falsified-%s-goes-quiet' % cls, left == [], [(x['line'], x['evidence'][:60]) for x in left])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # FIXTURES for the two detectors the corpus cannot falsify on its own: the corpus' only
    # check-cannot-fail case is Python, and its only test-replaces-subject case is an env override.
    # A detector without a negative fixture is a rumour.
    fix = tempfile.mkdtemp(prefix='silentfail_fixtures_')
    try:
        bad_sh = os.path.join(fix, 'bad.sh')
        open(bad_sh, 'w', encoding='utf-8', newline=chr(10)).write(
            '#!/bin/sh' + chr(10) + 'if [ -f /flag ]; then' + chr(10) +
            '    echo present' + chr(10) + '    exit 0' + chr(10) + 'else' + chr(10) +
            '    echo missing' + chr(10) + '    exit 0' + chr(10) + 'fi' + chr(10))
        good_sh = os.path.join(fix, 'good.sh')
        open(good_sh, 'w', encoding='utf-8', newline=chr(10)).write(
            '#!/bin/sh' + chr(10) + 'if [ -f /flag ]; then' + chr(10) +
            '    echo missing' + chr(10) + '    exit 3' + chr(10) + 'fi' + chr(10) + 'exit 0' + chr(10))
        check('shell-double-exit-fires',
              len(scan_check_cannot_fail_sh(bad_sh)) == 1, scan_check_cannot_fail_sh(bad_sh))
        check('shell-propagates-quiet',
              scan_check_cannot_fail_sh(good_sh) == [], scan_check_cannot_fail_sh(good_sh))

        # FIXTURES FOR THE TWO FIXES THE FALSIFIER FORCED. Running the linter cold on strangers'
        # repositories produced a false positive (a branch that raises, in poetry) and an
        # unusable evidence string (a 12-character slice, on dokku). Each fix gets the fixture
        # that would have caught it.
        raise_ok = os.path.join(fix, 'check_raise.py')
        open(raise_ok, 'w', encoding='utf-8', newline=chr(10)).write(
            'import sys' + chr(10) + 'def main():' + chr(10) +
            '    if len(sys.argv) < 2:' + chr(10) +
            "        raise SystemExit('usage: check_raise PATH')" + chr(10) +
            '    return 0' + chr(10))
        check('branch-that-raises-quiet',
              scan_check_cannot_fail_py(raise_ok) == [], scan_check_cannot_fail_py(raise_ok))

        swallow = os.path.join(fix, 'swallow.sh')
        open(swallow, 'w', encoding='utf-8', newline=chr(10)).write(
            '#!/bin/sh' + chr(10) + 'docker rm -f box >/dev/null 2>&1 || true' + chr(10))
        got_swallow = scan_check_cannot_fail_sh(swallow)
        check('swallowed-failure-quotes-the-command',
              len(got_swallow) == 1 and 'docker rm -f box' in got_swallow[0]['evidence'],
              [(f['line'], f['evidence']) for f in got_swallow])

        # FIXTURES FOR THE TWO STANDARD-LIBRARY FALSE POSITIVES. Eleven exported constants and
        # three healthy configparser guards were accused; both were the rule misreading what the
        # code does, and both keep the case that motivated the rule.
        pair = os.path.join(fix, 'interpolate.py')
        open(pair, 'w', encoding='utf-8', newline=chr(10)).write(
            'def before_set(value):' + chr(10) +
            "    tmp = value.replace('%%', '')" + chr(10) +
            "    if '%' in tmp:" + chr(10) +
            "        raise ValueError('bad interpolation')" + chr(10) +
            '    return value' + chr(10))
        check('doubled-pattern-strip-quiet',
              scan_dead_guard([pair]) == [], scan_dead_guard([pair]))
        single = os.path.join(fix, 'deadguard.py')
        open(single, 'w', encoding='utf-8', newline=chr(10)).write(
            'def f(value):' + chr(10) +
            "    tmp = value.replace('%', '')" + chr(10) +
            "    if '%' in tmp:" + chr(10) +
            '        return 1' + chr(10) +
            '    return 0' + chr(10))
        check('single-char-strip-fires',
              len(scan_dead_guard([single])) == 1, scan_dead_guard([single]))
        exported = os.path.join(fix, 'exported.py')
        open(exported, 'w', encoding='utf-8', newline=chr(10)).write(
            'ABORT = "abort"' + chr(10) +
            'if __name__ == "__main__":' + chr(10) + '    pass' + chr(10))
        check('exported-value-constant-quiet',
              scan_unread_constant(exported) == [], scan_unread_constant(exported))
        # THE PARSE CACHE MUST NOT SERVE A STALE TREE: scan a defective file, fix it, scan again.
        stale = os.path.join(fix, 'stale_check.py')
        body_bad = ('def f(value):' + chr(10) + "    tmp = value.replace('%', '')" + chr(10) +
                    "    if '%' in tmp:" + chr(10) + '        return 1' + chr(10) + '    return 0' + chr(10))
        open(stale, 'w', encoding='utf-8', newline=chr(10)).write(body_bad)
        before = len(scan_dead_guard([stale]))
        open(stale, 'w', encoding='utf-8', newline=chr(10)).write(
            body_bad.replace("replace('%', '')", "replace('%%', '')"))
        after = len(scan_dead_guard([stale]))
        check('parse-cache-not-stale', before > 0 and after == 0, (before, after))

        record = os.path.join(fix, 'fragment.py')
        open(record, 'w', encoding='utf-8', newline=chr(10)).write(
            'FRAG = "/tmp/frag.md"' + chr(10) +
            'if __name__ == "__main__":' + chr(10) + '    pass' + chr(10))
        check('unread-record-path-fires',
              len(scan_unread_constant(record)) == 1, scan_unread_constant(record))

        subj = os.path.join(fix, 'subject.py')
        open(subj, 'w', encoding='utf-8', newline=chr(10)).write(
            'import os' + chr(10) + 'def cmd():' + chr(10) +
            "    return os.environ.get('REAL_KEY', 'x')" + chr(10))
        bad_test = os.path.join(fix, 'test_bad.py')
        open(bad_test, 'w', encoding='utf-8', newline=chr(10)).write(
            'import os' + chr(10) + 'import subject' + chr(10) +
            "os.environ['REAL_KEY'] = 'true'" + chr(10) + 'def test_it():' + chr(10) +
            '    assert subject.cmd() == "true"' + chr(10))
        good_test = os.path.join(fix, 'test_good.py')
        open(good_test, 'w', encoding='utf-8', newline=chr(10)).write(
            'import subject' + chr(10) + 'def test_it(monkeypatch):' + chr(10) +
            '    monkeypatch.setenv("UNRELATED_KEY", "stub")' + chr(10) +
            '    assert subject.cmd() is not None' + chr(10))
        check('env-override-fires',
              len([f for f in scan_test_replaces_subject([subj, bad_test])
                   if os.path.basename(f['class']) and f['class'] == 'test-replaces-subject']) == 1,
              scan_test_replaces_subject([subj, bad_test]))
        check('unrelated-env-quiet',
              scan_test_replaces_subject([subj, good_test]) == [],
              scan_test_replaces_subject([subj, good_test]))

        # THREE RULES THE CORPUS' SECOND WAVE ADDED, each with the fixture that would have caught
        # it: an assembled shell needle must not look like a self-match, a cron script whose
        # check falls through to the file's own success return must fire, and a rebind of a
        # PRIVATE seam must stay quiet while a rebind of a public function plus an assertion on
        # that Mock must not.
        asm = os.path.join(fix, 'scan_marker.sh')
        open(asm, 'w', encoding='utf-8', newline=chr(10)).write(
            '#!/bin/sh' + chr(10) + 'ROOT=$(cd "$(dirname "$0")" && pwd)' + chr(10) +
            'MARKER=PLANTED_SECRET' + chr(10) +
            'if grep -r "$MARKER=" "$ROOT"; then' + chr(10) + '    exit 1' + chr(10) +
            'fi' + chr(10) + 'exit 0' + chr(10))
        check('assembled-needle-quiet', scan_control_reads_own_text(asm) == [],
              scan_control_reads_own_text(asm))

        cron = os.path.join(fix, 'diskcheck.py')
        open(cron, 'w', encoding='utf-8', newline=chr(10)).write(
            'import sys' + chr(10) + 'FLOOR_GB = 5' + chr(10) + chr(10) +
            'def main():' + chr(10) + '    free = 9' + chr(10) + '    if free < FLOOR_GB:' + chr(10) +
            '        print("LOW")' + chr(10) + '    return 0' + chr(10) + chr(10) +
            'if __name__ == "__main__":' + chr(10) + '    sys.exit(main())' + chr(10))
        hits = scan_check_cannot_fail_py(cron)
        check('py-fallthrough-fires', len(hits) == 1, hits)

        # THE IGNORED-STATUS RULE, in both directions. The defect is a verification whose result
        # decides nothing; the fix is the same call with the return code tested. The best-effort
        # cleanup in the fixed version proves the rule is about verifications, not subprocesses.
        ignored = os.path.join(fix, 'appender_bad.py')
        open(ignored, 'w', encoding='utf-8', newline=chr(10)).write(
            'import subprocess' + chr(10) + 'BACKUP = "/opt/backup.sh"' + chr(10) +
            'def append():' + chr(10) +
            '    for args in ([BACKUP], [BACKUP, "--verify"]):' + chr(10) +
            '        p = subprocess.run(args)' + chr(10) +
            '        print("rc=%d" % p.returncode)' + chr(10) + '    return 0' + chr(10))
        checked = os.path.join(fix, 'appender_fixed.py')
        open(checked, 'w', encoding='utf-8', newline=chr(10)).write(
            'import subprocess' + chr(10) + 'BACKUP = "/opt/backup.sh"' + chr(10) +
            'def append():' + chr(10) +
            '    for args in ([BACKUP], [BACKUP, "--verify"]):' + chr(10) +
            '        p = subprocess.run(args)' + chr(10) +
            '        print("rc=%d" % p.returncode)' + chr(10) +
            '        if p.returncode != 0:' + chr(10) + '            return 1' + chr(10) +
            '    subprocess.run(["rm", "-rf", "/tmp/x"], check=False)' + chr(10) +
            '    return 0' + chr(10))
        # THE DEAD GUARD AND THE UNREAD CONSTANT, each in both directions: the defect must be
        # reported and the near-miss must not, because a rule with only a positive case is a rumour.
        dg = os.path.join(fix, 'normalise_then_test.py')
        open(dg, 'w', encoding='utf-8', newline=chr(10)).write(
            'def read_norm(p):' + chr(10) +
            '    return open(p).read().replace(chr(13) + chr(10), chr(10)).replace(chr(13), chr(10))' + chr(10) +
            'def main(p):' + chr(10) + '    body = read_norm(p)' + chr(10) +
            '    if chr(13) in body:' + chr(10) + '        return 1' + chr(10) + '    return 0' + chr(10))
        # THE MASKED PIPELINE, both directions: under set -e without pipefail a grep piped into tail
        # cannot fail; with pipefail it can, and the rule must stay silent.
        mp = os.path.join(fix, 'appender_masked.sh')
        open(mp, 'w', encoding='utf-8', newline=chr(10)).write(
            '#!/bin/sh' + chr(10) + 'set -e' + chr(10) +
            'grep -o "^### " /tmp/ERRORS.md | tail -n 3' + chr(10) + 'echo done' + chr(10))
        check('masked-pipeline-fires', len(scan_masked_pipeline(mp)) == 1,
              scan_masked_pipeline(mp))
        mp_ok = os.path.join(fix, 'appender_pipefail.sh')
        open(mp_ok, 'w', encoding='utf-8', newline=chr(10)).write(
            '#!/bin/bash' + chr(10) + 'set -euo pipefail' + chr(10) +
            'grep -o "^### " /tmp/ERRORS.md | tail -n 3' + chr(10) + 'echo done' + chr(10))
        check('masked-pipeline-quiet-with-pipefail', scan_masked_pipeline(mp_ok) == [],
              scan_masked_pipeline(mp_ok))

        # THE PRINTED CHECK, both directions: a checkish script that prints a comparison and returns
        # 0 must be reported; the same script binding and testing the value must not.
        pc = os.path.join(fix, 'appender_printed.py')
        open(pc, 'w', encoding='utf-8', newline=chr(10)).write(
            'def main(f):' + chr(10) +
            '    heads = [ln for ln in open(f) if ln.startswith("#")]' + chr(10) +
            '    print("dup: %s" % (len(heads) != len(set(heads))))' + chr(10) +
            '    return 0' + chr(10))
        check('printed-check-fires', len(scan_printed_check(pc)) == 1, scan_printed_check(pc))
        pc_ok = os.path.join(fix, 'appender_tested.py')
        open(pc_ok, 'w', encoding='utf-8', newline=chr(10)).write(
            'def main(f):' + chr(10) +
            '    heads = [ln for ln in open(f) if ln.startswith("#")]' + chr(10) +
            '    dup = len(heads) != len(set(heads))' + chr(10) +
            '    print("dup: %s" % dup)' + chr(10) + '    if dup:' + chr(10) +
            '        return 1' + chr(10) + '    return 0' + chr(10))
        check('printed-check-quiet-when-tested', scan_printed_check(pc_ok) == [],
              scan_printed_check(pc_ok))

        check('dead-guard-fires', len(scan_dead_guard([dg])) == 1, scan_dead_guard([dg]))
        dg_ok = os.path.join(fix, 'guard_that_can_fire.py')
        open(dg_ok, 'w', encoding='utf-8', newline=chr(10)).write(
            'def read_norm(p):' + chr(10) +
            '    return open(p).read().replace(chr(13) + chr(10), chr(10))' + chr(10) +
            'def main(p):' + chr(10) + '    body = read_norm(p)' + chr(10) +
            '    if not body.endswith(chr(10)):' + chr(10) + '        return 1' + chr(10) + '    return 0' + chr(10))
        check('dead-guard-quiet-when-the-guard-can-fire', scan_dead_guard([dg_ok]) == [],
              scan_dead_guard([dg_ok]))
        # THE SCOPE-CHAIN FIXTURE, ON ITS OWN, because it is the one case the obvious optimisation
        # breaks. This detector attributes an assignment to EVERY function that encloses it, not
        # only the innermost one, since an outer normalisation is exactly what a nested guard reads.
        # Rewriting it to attach each assignment to its innermost scope keeps every other check here
        # green and silently loses this finding, so the nested shape is pinned separately.
        dg_nested = os.path.join(fix, 'normalise_then_test_nested.py')
        open(dg_nested, 'w', encoding='utf-8', newline=chr(10)).write(
            'def read_norm(p):' + chr(10) +
            '    return open(p).read().replace(chr(13) + chr(10), chr(10)).replace(chr(13), chr(10))' + chr(10) +
            'def main(p):' + chr(10) + '    body = read_norm(p)' + chr(10) +
            '    def report():' + chr(10) + '        if chr(13) in body:' + chr(10) +
            '            return "crlf"' + chr(10) + '        return "clean"' + chr(10) +
            '    return report()' + chr(10))
        check('dead-guard-fires-across-a-nested-scope',
              len(scan_dead_guard([dg_nested])) == 1, scan_dead_guard([dg_nested]))
        uc = os.path.join(fix, 'fragment_pair.py')
        open(uc, 'w', encoding='utf-8', newline=chr(10)).write(
            'FE, FH = "/tmp/e.md", "/tmp/h.md"' + chr(10) + 'def main():' + chr(10) +
            '    print(open(FE).read())' + chr(10) + '    return 0' + chr(10) +
            'if __name__ == "__main__":' + chr(10) + '    main()' + chr(10))
        check('unread-constant-fires', len(scan_unread_constant(uc)) == 1,
              scan_unread_constant(uc))
        uc_ok = os.path.join(fix, 'fragment_pair_used.py')
        open(uc_ok, 'w', encoding='utf-8', newline=chr(10)).write(
            'FE, FH = "/tmp/e.md", "/tmp/h.md"' + chr(10) + 'def main():' + chr(10) +
            '    print(open(FE).read(), open(FH).read())' + chr(10) + '    return 0' + chr(10) +
            'if __name__ == "__main__":' + chr(10) + '    main()' + chr(10))
        check('unread-constant-quiet-when-used', scan_unread_constant(uc_ok) == [],
              scan_unread_constant(uc_ok))

        check('ignored-status-fires', len(scan_check_cannot_fail_py(ignored)) == 1,
              scan_check_cannot_fail_py(ignored))
        check('tested-status-quiet', scan_check_cannot_fail_py(checked) == [],
              scan_check_cannot_fail_py(checked))

        seam = os.path.join(fix, 'probe.py')
        open(seam, 'w', encoding='utf-8', newline=chr(10)).write(
            'def _raw():' + chr(10) + '    return 1' + chr(10) + chr(10) +
            'def check():' + chr(10) + '    return _raw()' + chr(10))
        quiet = os.path.join(fix, 'test_seam.py')
        open(quiet, 'w', encoding='utf-8', newline=chr(10)).write(
            'import probe' + chr(10) + 'def test_check(monkeypatch):' + chr(10) +
            '    monkeypatch.setattr(probe, "_raw", lambda: 3)' + chr(10) +
            '    assert probe.check() == 3' + chr(10))
        check('private-seam-quiet', scan_test_replaces_subject([seam, quiet]) == [],
              scan_test_replaces_subject([seam, quiet]))
        loud = os.path.join(fix, 'test_rebind.py')
        open(loud, 'w', encoding='utf-8', newline=chr(10)).write(
            'from unittest import mock' + chr(10) + 'import probe' + chr(10) +
            'def test_check():' + chr(10) + '    probe.check = mock.Mock(return_value=0)' + chr(10) +
            '    probe.check()' + chr(10) + '    probe.check.assert_called_once()' + chr(10))
        check('public-rebind-fires', len(scan_test_replaces_subject([seam, loud])) == 1,
              scan_test_replaces_subject([seam, loud]))

        writer = os.path.join(fix, 'writer.py')
        open(writer, 'w', encoding='utf-8', newline=chr(10)).write(
            'import os' + chr(10) + 'LEDGER = os.path.join(os.path.expanduser(chr(126)), '
            "'state', 'rows.jsonl')" + chr(10))
        # THE LONELY READER HAS TO READ. The fixture used to be nothing but the literal, and the
        # rule that requires an I/O verb - correctly - went quiet on it: a path literal nothing
        # opens is not a reader, which is the whole estate_notify.py false positive.
        lonely = os.path.join(fix, 'lonely.py')
        open(lonely, 'w', encoding='utf-8', newline=chr(10)).write(
            'import os' + chr(10) + "PATH = '/var/lib/state/rows.jsonl'" + chr(10) +
            'def count():' + chr(10) + '    with open(PATH) as fh:' + chr(10) +
            '        return sum(1 for _ in fh)' + chr(10))
        check('record-unread-fires',
              len(scan_record_unread([writer, lonely])) == 1, scan_record_unread([writer, lonely]))
        same = os.path.join(fix, 'same.py')
        open(same, 'w', encoding='utf-8', newline=chr(10)).write(
            'import os' + chr(10) + "PATH = '/home/svc/state/rows.jsonl'" + chr(10) +
            'def count():' + chr(10) + '    with open(PATH) as fh:' + chr(10) +
            '        return 1' + chr(10))
        open(writer, 'w', encoding='utf-8', newline=chr(10)).write(
            'import os' + chr(10) + "LEDGER = '/home/svc/state/rows.jsonl'" + chr(10))
        check('record-unread-quiet-when-paths-agree',
              scan_record_unread([writer, same]) == [], scan_record_unread([writer, same]))

        # THE RULE THAT REQUIRES A READ, WITH THE TWO FIXTURES THAT FALSIFY IT: a path literal
        # nothing opens must stay quiet, and so must a placeholder home path that a self-test
        # passes to a validator.
        unread = os.path.join(fix, 'mentions.py')
        open(unread, 'w', encoding='utf-8', newline=chr(10)).write(
            'import os' + chr(10) + "EXAMPLE = '/var/lib/state/rows.jsonl'" + chr(10) +
            'def describe():' + chr(10) + '    return EXAMPLE' + chr(10))
        check('path-literal-not-read-quiet', scan_record_unread([writer, unread]) == [],
              scan_record_unread([writer, unread]))
        fixture = os.path.join(fix, 'fixture.py')
        open(fixture, 'w', encoding='utf-8', newline=chr(10)).write(
            'import json' + chr(10) + "def classify(rows):" + chr(10) +
            '    with open(rows[0], encoding="utf-8") as fh:' + chr(10) +
            '        return json.load(fh)' + chr(10) +
            "classify(['/home/x/state/rows.jsonl'])" + chr(10))
        check('placeholder-home-path-quiet', scan_record_unread([writer, fixture]) == [],
              scan_record_unread([writer, fixture]))

        # AND A TEST THAT READS THE DEPLOYED PATH IS DOING ITS JOB, not standing in for a reader
        # that will run. test_oom_delta.py does exactly this and cost two production files a
        # high-confidence accusation.
        testread = os.path.join(fix, 'test_reader.py')
        open(testread, 'w', encoding='utf-8', newline=chr(10)).write(
            'import json' + chr(10) + "S = '/var/lib/state/rows.jsonl'" + chr(10) +
            'def state():' + chr(10) + '    return json.load(open(S))' + chr(10))
        check('test-reader-quiet', scan_record_unread([writer, testread]) == [],
              scan_record_unread([writer, testread]))
    finally:
        shutil.rmtree(fix, ignore_errors=True)

    if planted:
        shutil.rmtree(planted, ignore_errors=True)

    # The linter must survive what it cannot read.
    junk = tempfile.mkdtemp(prefix='silentfail_junk_')
    try:
        open(os.path.join(junk, 'broken.py'), 'w', encoding='utf-8').write('def (:\n')
        open(os.path.join(junk, 'binary.dat'), 'wb').write(bytes(range(256)))
        open(os.path.join(junk, 'ok.py'), 'w', encoding='utf-8').write('x = 1\n')
        try:
            f2, sk, _wk2 = scan([junk])
            check('survives-unreadable', True)
            check('counts-skipped', sk >= 1, sk)
        except Exception as exc:                                # noqa: BLE001
            check('survives-unreadable', False, '%s: %s' % (type(exc).__name__, exc))
    finally:
        shutil.rmtree(junk, ignore_errors=True)

    check('exit-code-claims-findings', (1 if findings else 0) == 1)
    print('silentfail selftest: %d ok, %d failed' % (ok, fail))
    for n in notes:
        print(n)
    return 0 if fail == 0 else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if '--selftest' in argv:
        return selftest()
    as_json = '--json' in argv
    # HIGH BY DEFAULT. A first run on 3,821 real Python files returned 410 findings, 363 of them
    # medium-confidence, and a tool that greets you with 363 maybes is a tool you filter out. The
    # aggressive rules are one flag away and are honest about being maybes.
    floor = 'high'
    for a in argv:
        if a.startswith('--min-confidence='):
            floor = a.split('=', 1)[1]
    rank = {'low': 0, 'medium': 1, 'high': 2}
    paths = [a for a in argv if not a.startswith('--')]
    if not paths:
        print(__doc__)
        return 2
    missing = [p for p in paths if not os.path.exists(p)]
    if missing:
        print('REFUSING: no such path: %s' % ', '.join(missing))
        return 2
    max_bytes = None
    walk_all = '--include-all' in argv
    for a in argv:
        if a.startswith('--max-bytes='):
            max_bytes = int(a.split('=', 1)[1])
    findings, skipped, walked = scan(paths, max_bytes=max_bytes, walk_all=walk_all)
    # EXPLICIT FILES ARE FILES SCANNED. `silentfail some/check.sh` printed a finding and then
    # '(0 file(s) scanned)' on the next line, which is the linter contradicting itself in its own
    # output - the exact category it exists to find.
    walked += len([p for p in paths if os.path.isfile(p)])
    findings = [f for f in findings if rank.get(f['confidence'], 0) >= rank.get(floor, 0)]
    if as_json:
        print(json.dumps({'findings': findings, 'skipped_files': skipped, 'files_walked': walked},
                         indent=2, sort_keys=True))
    else:
        print(report(findings, paths))
        print('(%d file(s) scanned, %d skipped by size or exclusion)' % (walked, skipped))
    return 1 if findings else 0


if __name__ == '__main__':
    sys.exit(main())
