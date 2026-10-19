"""corpus_data.py - the certification corpus as data, shipped inside the installed package.

It lives in a module rather than a JSON file because the corpus has to travel with a tool that can
be pip-installed: a selftest that refuses to run on a machine without the bench directory is the
same silent-pass defect this linter exists to find.

Each case is a directory of files. Each truth contract names the class, the file, the needle inside
it, and the line the finding must land within three of.
"""
CASES = {'append_verified': {'appender.py': '"""Append one entry to a memory file, replicate it, and fail '
                                    'when replication fails."""\n'
                                    'import os\n'
                                    'import subprocess\n'
                                    'import sys\n'
                                    '\n'
                                    'MEMORY = "/srv/memory/ERRORS.md"\n'
                                    'BACKUP = "/opt/tools/memory_backup.sh"\n'
                                    'SCRATCH = "/tmp/memory_append.work"\n'
                                    '\n'
                                    '\n'
                                    'def append(fragment):\n'
                                    '    if not os.path.exists(fragment):\n'
                                    '        print("missing fragment")\n'
                                    '        return 1\n'
                                    '    with open(MEMORY, "a", encoding="utf-8") as fh:\n'
                                    '        fh.write(open(fragment, encoding="utf-8").read())\n'
                                    '    for args in ([BACKUP], [BACKUP, "--verify"]):\n'
                                    '        p = subprocess.run(args)\n'
                                    '        print("rc=%d %s" % (p.returncode, " ".join(args)))\n'
                                    '        if p.returncode != 0:\n'
                                    '            print("FAILED: %s returned %d" % (" ".join(args), '
                                    'p.returncode))\n'
                                    '            return 1\n'
                                    '    # best effort: the scratch directory is a convenience, '
                                    'losing it is not a failure\n'
                                    '    subprocess.run(["rm", "-rf", SCRATCH], check=False)\n'
                                    '    return 0\n'
                                    '\n'
                                    '\n'
                                    'if __name__ == "__main__":\n'
                                    '    sys.exit(append(sys.argv[1]))\n'
                                    '\n'},
 'append_verified_ren': {'appender.py': '"""Append one entry to a memory file, replicate it, and '
                                        'fail when replication fails."""\n'
                                        'import os\n'
                                        'import subprocess\n'
                                        'import sys\n'
                                        '\n'
                                        'MEMORY_v2 = "/srv/memory/ERRORS.md"\n'
                                        'BACKUP_v2 = "/opt/tools/memory_backup.sh"\n'
                                        'SCRATCH_v2 = "/tmp/memory_append.work"\n'
                                        '\n'
                                        '\n'
                                        'def append_v2(fragment):\n'
                                        '    if not os.path.exists(fragment):\n'
                                        '        print("missing fragment")\n'
                                        '        return 1\n'
                                        '    with open(MEMORY_v2, "a", encoding="utf-8") as fh:\n'
                                        '        fh.write(open(fragment, '
                                        'encoding="utf-8").read())\n'
                                        '    for args in ([BACKUP_v2], [BACKUP_v2, "--verify"]):\n'
                                        '        p = subprocess.run(args)\n'
                                        '        print("rc=%d %s" % (p.returncode, " '
                                        '".join(args)))\n'
                                        '        if p.returncode != 0:\n'
                                        '            print("FAILED: %s returned %d" % (" '
                                        '".join(args), p.returncode))\n'
                                        '            return 1\n'
                                        '    # best effort: the scratch directory is a '
                                        'convenience, losing it is not a failure\n'
                                        '    subprocess.run(["rm", "-rf", SCRATCH_v2], '
                                        'check=False)\n'
                                        '    return 0\n'
                                        '\n'
                                        '\n'
                                        'if __name__ == "__main__":\n'
                                        '    sys.exit(append_v2(sys.argv[1]))\n'
                                        '\n'},
 'append_verified_svc': {'svc/appender.py': '"""Append one entry to a memory file, replicate it, '
                                            'and fail when replication fails."""\n'
                                            'import os\n'
                                            'import subprocess\n'
                                            'import sys\n'
                                            '\n'
                                            'MEMORY = "/srv/memory/ERRORS.md"\n'
                                            'BACKUP = "/opt/tools/memory_backup.sh"\n'
                                            'SCRATCH = "/tmp/memory_append.work"\n'
                                            '\n'
                                            '\n'
                                            'def append(fragment):\n'
                                            '    if not os.path.exists(fragment):\n'
                                            '        print("missing fragment")\n'
                                            '        return 1\n'
                                            '    with open(MEMORY, "a", encoding="utf-8") as fh:\n'
                                            '        fh.write(open(fragment, '
                                            'encoding="utf-8").read())\n'
                                            '    for args in ([BACKUP], [BACKUP, "--verify"]):\n'
                                            '        p = subprocess.run(args)\n'
                                            '        print("rc=%d %s" % (p.returncode, " '
                                            '".join(args)))\n'
                                            '        if p.returncode != 0:\n'
                                            '            print("FAILED: %s returned %d" % (" '
                                            '".join(args), p.returncode))\n'
                                            '            return 1\n'
                                            '    # best effort: the scratch directory is a '
                                            'convenience, losing it is not a failure\n'
                                            '    subprocess.run(["rm", "-rf", SCRATCH], '
                                            'check=False)\n'
                                            '    return 0\n'
                                            '\n'
                                            '\n'
                                            'if __name__ == "__main__":\n'
                                            '    sys.exit(append(sys.argv[1]))\n'
                                            '\n'},
 'audit_ignored': {'admin.py': '"""The maintainer page counts what the writer appended."""\n'
                               'from store import LOG\n'
                               '\n'
                               '\n'
                               'def count():\n'
                               '    if not LOG.exists():\n'
                               '        return 0\n'
                               '    with open(LOG, encoding="utf-8") as fh:\n'
                               '        return sum(1 for line in fh if line.strip())\n'
                               '\n',
                   'audit.service': '[Unit]\n'
                                    'Description=audit appender\n'
                                    '\n'
                                    '[Service]\n'
                                    'Type=oneshot\n'
                                    'User=deploy\n'
                                    'ExecStart=/usr/bin/python3 /opt/app/store.py\n'
                                    '\n',
                   'report.py': '"""The nightly report counts audit rows for the same run."""\n'
                                'LEDGER = "/srv/app/audit.jsonl"\n'
                                '\n'
                                '\n'
                                'def count():\n'
                                '    with open(LEDGER, encoding="utf-8") as fh:\n'
                                '        return sum(1 for line in fh if line.strip())\n'
                                '\n',
                   'store.py': '"""Append one audit row per run; this module decides the path."""\n'
                               'import json\n'
                               'from pathlib import Path\n'
                               '\n'
                               'LOG = Path.home() / ".local" / "state" / "app" / "audit.jsonl"\n'
                               '\n'
                               '\n'
                               'def append(row):\n'
                               '    LOG.parent.mkdir(parents=True, exist_ok=True)\n'
                               '    with open(LOG, "a", encoding="utf-8") as fh:\n'
                               '        fh.write(json.dumps(row) + chr(10))\n'
                               '\n'},
 'audit_ignored_ren': {'admin.py': '"""The maintainer page counts what the writer appended."""\n'
                                   'from store import LOG_v2\n'
                                   '\n'
                                   '\n'
                                   'def count_v2():\n'
                                   '    if not LOG_v2.exists():\n'
                                   '        return 0\n'
                                   '    with open(LOG_v2, encoding="utf-8") as fh:\n'
                                   '        return sum(1 for line in fh if line.strip())\n'
                                   '\n',
                       'audit.service': '[Unit]\n'
                                        'Description=audit appender\n'
                                        '\n'
                                        '[Service]\n'
                                        'Type=oneshot\n'
                                        'User=deploy\n'
                                        'ExecStart=/usr/bin/python3 /opt/app/store.py\n'
                                        '\n',
                       'report.py': '"""The nightly report counts audit rows for the same run."""\n'
                                    'LEDGER_v2 = "/srv/app/audit.jsonl"\n'
                                    '\n'
                                    '\n'
                                    'def count_v2():\n'
                                    '    with open(LEDGER_v2, encoding="utf-8") as fh:\n'
                                    '        return sum(1 for line in fh if line.strip())\n'
                                    '\n',
                       'store.py': '"""Append one audit row per run; this module decides the '
                                   'path."""\n'
                                   'import json\n'
                                   'from pathlib import Path\n'
                                   '\n'
                                   'LOG_v2 = Path.home() / ".local" / "state" / "app" / '
                                   '"audit.jsonl"\n'
                                   '\n'
                                   '\n'
                                   'def append_v2(row):\n'
                                   '    LOG_v2.parent.mkdir(parents=True, exist_ok=True)\n'
                                   '    with open(LOG_v2, "a", encoding="utf-8") as fh:\n'
                                   '        fh.write(json.dumps(row) + chr(10))\n'
                                   '\n'},
 'audit_ignored_svc': {'svc/admin.py': '"""The maintainer page counts what the writer '
                                       'appended."""\n'
                                       'from store import LOG\n'
                                       '\n'
                                       '\n'
                                       'def count():\n'
                                       '    if not LOG.exists():\n'
                                       '        return 0\n'
                                       '    with open(LOG, encoding="utf-8") as fh:\n'
                                       '        return sum(1 for line in fh if line.strip())\n'
                                       '\n',
                       'svc/audit.service': '[Unit]\n'
                                            'Description=audit appender\n'
                                            '\n'
                                            '[Service]\n'
                                            'Type=oneshot\n'
                                            'User=deploy\n'
                                            'ExecStart=/usr/bin/python3 /opt/app/store.py\n'
                                            '\n',
                       'svc/report.py': '"""The nightly report counts audit rows for the same '
                                        'run."""\n'
                                        'LEDGER = "/srv/app/audit.jsonl"\n'
                                        '\n'
                                        '\n'
                                        'def count():\n'
                                        '    with open(LEDGER, encoding="utf-8") as fh:\n'
                                        '        return sum(1 for line in fh if line.strip())\n'
                                        '\n',
                       'svc/store.py': '"""Append one audit row per run; this module decides the '
                                       'path."""\n'
                                       'import json\n'
                                       'from pathlib import Path\n'
                                       '\n'
                                       'LOG = Path.home() / ".local" / "state" / "app" / '
                                       '"audit.jsonl"\n'
                                       '\n'
                                       '\n'
                                       'def append(row):\n'
                                       '    LOG.parent.mkdir(parents=True, exist_ok=True)\n'
                                       '    with open(LOG, "a", encoding="utf-8") as fh:\n'
                                       '        fh.write(json.dumps(row) + chr(10))\n'
                                       '\n'},
 'check_units': {'check_units.sh': '#!/bin/sh\n'
                                   '# Cron calls this every five minutes. The exit status is the '
                                   'only thing anyone reads.\n'
                                   'if systemctl is-active --quiet estate-heartbeat.service; then\n'
                                   '    echo "heartbeat active"\n'
                                   'else\n'
                                   '    echo "HEARTBEAT DOWN"\n'
                                   '    exit 0\n'
                                   'fi\n'
                                   '\n',
                 'crontab.txt': '*/5 * * * * /opt/estate/check_units.sh\n\n'},
 'check_units_svc': {'svc/check_units.sh': '#!/bin/sh\n'
                                           '# Cron calls this every five minutes. The exit status '
                                           'is the only thing anyone reads.\n'
                                           'if systemctl is-active --quiet '
                                           'estate-heartbeat.service; then\n'
                                           '    echo "heartbeat active"\n'
                                           'else\n'
                                           '    echo "HEARTBEAT DOWN"\n'
                                           '    exit 0\n'
                                           'fi\n'
                                           '\n',
                     'svc/crontab.txt': '*/5 * * * * /opt/estate/check_units.sh\n\n'},
 'checksum_guard': {'main.py': '"""Exit 0 only when the digest matches; 2 for either failure."""\n'
                               'import sys\n'
                               '\n'
                               'from verify import matches\n'
                               '\n'
                               '\n'
                               'def main(argv):\n'
                               '    if len(argv) != 2:\n'
                               '        print("usage: main.py FILE SHA256")\n'
                               '        return 2\n'
                               '    try:\n'
                               '        ok = matches(argv[0], argv[1])\n'
                               '    except FileNotFoundError:\n'
                               '        print("missing file")\n'
                               '        return 2\n'
                               '    if not ok:\n'
                               '        print("checksum mismatch")\n'
                               '        return 2\n'
                               '    return 0\n'
                               '\n'
                               '\n'
                               'if __name__ == "__main__":\n'
                               '    sys.exit(main(sys.argv[1:]))\n'
                               '\n',
                    'verify.py': '"""Return True only when the file digest matches the expected '
                                 'one."""\n'
                                 'import hashlib\n'
                                 '\n'
                                 'BLOCK = 65536\n'
                                 '\n'
                                 '\n'
                                 'def matches(path, expected):\n'
                                 '    h = hashlib.sha256()\n'
                                 '    with open(path, "rb") as fh:\n'
                                 '        for block in iter(lambda: fh.read(BLOCK), b""):\n'
                                 '            h.update(block)\n'
                                 '    return h.hexdigest() == expected\n'
                                 '\n'},
 'checksum_guard_ren': {'main.py': '"""Exit 0 only when the digest matches_v2; 2 for either '
                                   'failure."""\n'
                                   'import sys\n'
                                   '\n'
                                   'from verify import matches_v2\n'
                                   '\n'
                                   '\n'
                                   'def main(argv):\n'
                                   '    if len(argv) != 2:\n'
                                   '        print("usage: main.py FILE SHA256")\n'
                                   '        return 2\n'
                                   '    try:\n'
                                   '        ok = matches_v2(argv[0], argv[1])\n'
                                   '    except FileNotFoundError:\n'
                                   '        print("missing file")\n'
                                   '        return 2\n'
                                   '    if not ok:\n'
                                   '        print("checksum mismatch")\n'
                                   '        return 2\n'
                                   '    return 0\n'
                                   '\n'
                                   '\n'
                                   'if __name__ == "__main__":\n'
                                   '    sys.exit(main(sys.argv[1:]))\n'
                                   '\n',
                        'verify.py': '"""Return True only when the file digest matches_v2 the '
                                     'expected one."""\n'
                                     'import hashlib\n'
                                     '\n'
                                     'BLOCK_v2 = 65536\n'
                                     '\n'
                                     '\n'
                                     'def matches_v2(path, expected):\n'
                                     '    h = hashlib.sha256()\n'
                                     '    with open(path, "rb") as fh:\n'
                                     '        for block in iter(lambda: fh.read(BLOCK_v2), b""):\n'
                                     '            h.update(block)\n'
                                     '    return h.hexdigest() == expected\n'
                                     '\n'},
 'checksum_guard_svc': {'svc/main.py': '"""Exit 0 only when the digest matches; 2 for either '
                                       'failure."""\n'
                                       'import sys\n'
                                       '\n'
                                       'from verify import matches\n'
                                       '\n'
                                       '\n'
                                       'def main(argv):\n'
                                       '    if len(argv) != 2:\n'
                                       '        print("usage: main.py FILE SHA256")\n'
                                       '        return 2\n'
                                       '    try:\n'
                                       '        ok = matches(argv[0], argv[1])\n'
                                       '    except FileNotFoundError:\n'
                                       '        print("missing file")\n'
                                       '        return 2\n'
                                       '    if not ok:\n'
                                       '        print("checksum mismatch")\n'
                                       '        return 2\n'
                                       '    return 0\n'
                                       '\n'
                                       '\n'
                                       'if __name__ == "__main__":\n'
                                       '    sys.exit(main(sys.argv[1:]))\n'
                                       '\n',
                        'svc/verify.py': '"""Return True only when the file digest matches the '
                                         'expected one."""\n'
                                         'import hashlib\n'
                                         '\n'
                                         'BLOCK = 65536\n'
                                         '\n'
                                         '\n'
                                         'def matches(path, expected):\n'
                                         '    h = hashlib.sha256()\n'
                                         '    with open(path, "rb") as fh:\n'
                                         '        for block in iter(lambda: fh.read(BLOCK), b""):\n'
                                         '            h.update(block)\n'
                                         '    return h.hexdigest() == expected\n'
                                         '\n'},
 'disk_guard': {'check_disk.py': '"""Nightly disk guard: verify the root filesystem stays under '
                                 'its configured limit."""\n'
                                 'import json\n'
                                 'import shutil\n'
                                 '\n'
                                 "LIMIT = json.load(open('limits.json'))['disk_pct']\n"
                                 '\n'
                                 '\n'
                                 'def check():\n'
                                 "    total, used, free = shutil.disk_usage('/')\n"
                                 '    pct = used / total * 100\n'
                                 '    if pct > LIMIT:\n'
                                 "        print('DISK-OVER-LIMIT pct=%.1f limit=%s' % (pct, "
                                 'LIMIT))\n'
                                 '        return 0\n'
                                 "    print('disk ok pct=%.1f limit=%s' % (pct, LIMIT))\n"
                                 '    return 0\n'
                                 '\n'
                                 '\n'
                                 "if __name__ == '__main__':\n"
                                 '    raise SystemExit(check())\n',
                'limits.json': '{"disk_pct": 90}',
                'run_check.sh': '#!/bin/sh\n'
                                '# Called by cron every hour. The caller reads the exit status; '
                                'stdout goes to the journal\n'
                                '# and nobody subscribes to it.\n'
                                'python3 check_disk.py\n'
                                'status=$?\n'
                                'if [ "$status" -eq 0 ]; then\n'
                                '    echo "DISK-GUARD OK status=$status" >> '
                                '/var/log/disk_guard.log\n'
                                'fi\n'
                                'exit $status\n'},
 'disk_guard_ren': {'check_disk.py': '"""Nightly disk guard: verify the root filesystem stays '
                                     'under its configured limit."""\n'
                                     'import json\n'
                                     'import shutil\n'
                                     '\n'
                                     "LIMIT = json.load(open('limits.json'))['disk_pct']\n"
                                     '\n'
                                     '\n'
                                     'def check_v2():\n'
                                     "    total, used, free = shutil.disk_usage('/')\n"
                                     '    pct = used / total * 100\n'
                                     '    if pct > LIMIT:\n'
                                     "        print('DISK-OVER-LIMIT pct=%.1f limit=%s' % (pct, "
                                     'LIMIT))\n'
                                     '        return 0\n'
                                     "    print('disk ok pct=%.1f limit=%s' % (pct, LIMIT))\n"
                                     '    return 0\n'
                                     '\n'
                                     '\n'
                                     "if __name__ == '__main__':\n"
                                     '    raise SystemExit(check_v2())\n',
                    'limits.json': '{"disk_pct": 90}',
                    'run_check.sh': '#!/bin/sh\n'
                                    '# Called by cron every hour. The caller reads the exit '
                                    'status; stdout goes to the journal\n'
                                    '# and nobody subscribes to it.\n'
                                    'python3 check_disk.py\n'
                                    'status=$?\n'
                                    'if [ "$status" -eq 0 ]; then\n'
                                    '    echo "DISK-GUARD OK status=$status" >> '
                                    '/var/log/disk_guard.log\n'
                                    'fi\n'
                                    'exit $status\n'},
 'disk_guard_svc': {'svc/check_disk.py': '"""Nightly disk guard: verify the root filesystem stays '
                                         'under its configured limit."""\n'
                                         'import json\n'
                                         'import shutil\n'
                                         '\n'
                                         "LIMIT = json.load(open('limits.json'))['disk_pct']\n"
                                         '\n'
                                         '\n'
                                         'def check():\n'
                                         "    total, used, free = shutil.disk_usage('/')\n"
                                         '    pct = used / total * 100\n'
                                         '    if pct > LIMIT:\n'
                                         "        print('DISK-OVER-LIMIT pct=%.1f limit=%s' % "
                                         '(pct, LIMIT))\n'
                                         '        return 0\n'
                                         "    print('disk ok pct=%.1f limit=%s' % (pct, LIMIT))\n"
                                         '    return 0\n'
                                         '\n'
                                         '\n'
                                         "if __name__ == '__main__':\n"
                                         '    raise SystemExit(check())\n',
                    'svc/limits.json': '{"disk_pct": 90}',
                    'svc/run_check.sh': '#!/bin/sh\n'
                                        '# Called by cron every hour. The caller reads the exit '
                                        'status; stdout goes to the journal\n'
                                        '# and nobody subscribes to it.\n'
                                        'python3 check_disk.py\n'
                                        'status=$?\n'
                                        'if [ "$status" -eq 0 ]; then\n'
                                        '    echo "DISK-GUARD OK status=$status" >> '
                                        '/var/log/disk_guard.log\n'
                                        'fi\n'
                                        'exit $status\n'},
 'env_default_agrees': {'checker.py': '"""Say whether a resolved URL is the shipped default."""\n'
                                      'from settings import DEFAULT_ENDPOINT\n'
                                      '\n'
                                      '\n'
                                      'def is_default(url):\n'
                                      '    return url == DEFAULT_ENDPOINT\n'
                                      '\n',
                        'endpoint.py': '"""Resolve the collect URL, allowing an override from the '
                                       'environment."""\n'
                                       'import os\n'
                                       '\n'
                                       'from settings import DEFAULT_ENDPOINT\n'
                                       '\n'
                                       '\n'
                                       'def resolve():\n'
                                       '    return os.environ.get("COLLECT_URL") or '
                                       'DEFAULT_ENDPOINT\n'
                                       '\n',
                        'settings.py': '"""One constant, imported everywhere the collect URL is '
                                       'needed."""\n'
                                       'DEFAULT_ENDPOINT = "https://api.internal/collect"\n'
                                       '\n'},
 'env_default_agrees_ren': {'checker.py': '"""Say whether a resolved URL is the shipped '
                                          'default."""\n'
                                          'from settings import DEFAULT_ENDPOINT\n'
                                          '\n'
                                          '\n'
                                          'def is_default_v2(url):\n'
                                          '    return url == DEFAULT_ENDPOINT\n'
                                          '\n',
                            'endpoint.py': '"""Resolve the collect URL, allowing an override from '
                                           'the environment."""\n'
                                           'import os\n'
                                           '\n'
                                           'from settings import DEFAULT_ENDPOINT\n'
                                           '\n'
                                           '\n'
                                           'def resolve_v2():\n'
                                           '    return os.environ.get("COLLECT_URL") or '
                                           'DEFAULT_ENDPOINT\n'
                                           '\n',
                            'settings.py': '"""One constant, imported everywhere the collect URL '
                                           'is needed."""\n'
                                           'DEFAULT_ENDPOINT = "https://api.internal/collect"\n'
                                           '\n'},
 'env_default_agrees_svc': {'svc/checker.py': '"""Say whether a resolved URL is the shipped '
                                              'default."""\n'
                                              'from settings import DEFAULT_ENDPOINT\n'
                                              '\n'
                                              '\n'
                                              'def is_default(url):\n'
                                              '    return url == DEFAULT_ENDPOINT\n'
                                              '\n',
                            'svc/endpoint.py': '"""Resolve the collect URL, allowing an override '
                                               'from the environment."""\n'
                                               'import os\n'
                                               '\n'
                                               'from settings import DEFAULT_ENDPOINT\n'
                                               '\n'
                                               '\n'
                                               'def resolve():\n'
                                               '    return os.environ.get("COLLECT_URL") or '
                                               'DEFAULT_ENDPOINT\n'
                                               '\n',
                            'svc/settings.py': '"""One constant, imported everywhere the collect '
                                               'URL is needed."""\n'
                                               'DEFAULT_ENDPOINT = "https://api.internal/collect"\n'
                                               '\n'},
 'fragment_pair': {'appender.py': '"""Append the errors fragment and the history fragment."""\n'
                                  'import sys\n'
                                  '\n'
                                  'FE, FH = "/tmp/_errors.md", "/tmp/_history.md"\n'
                                  'ERRORS = "/srv/memory/ERRORS.md"\n'
                                  '\n'
                                  '\n'
                                  'def append(fragment, target):\n'
                                  '    with open(target, "a", encoding="utf-8") as fh:\n'
                                  '        fh.write(open(fragment, encoding="utf-8").read())\n'
                                  '\n'
                                  '\n'
                                  'def main():\n'
                                  '    append(FE, ERRORS)\n'
                                  '    print("errors appended")\n'
                                  '    return 0\n'
                                  '\n'
                                  '\n'
                                  'if __name__ == "__main__":\n'
                                  '    sys.exit(main())\n'
                                  '\n'},
 'fragment_pair_ren': {'appender.py': '"""Append the errors fragment and the history fragment."""\n'
                                      'import sys\n'
                                      '\n'
                                      'FE, FH = "/tmp/_errors.md", "/tmp/_history.md"\n'
                                      'ERRORS_v2 = "/srv/memory/ERRORS_v2.md"\n'
                                      '\n'
                                      '\n'
                                      'def append_v2(fragment, target):\n'
                                      '    with open(target, "a", encoding="utf-8") as fh:\n'
                                      '        fh.write(open(fragment, encoding="utf-8").read())\n'
                                      '\n'
                                      '\n'
                                      'def main():\n'
                                      '    append_v2(FE, ERRORS_v2)\n'
                                      '    print("errors appended")\n'
                                      '    return 0\n'
                                      '\n'
                                      '\n'
                                      'if __name__ == "__main__":\n'
                                      '    sys.exit(main())\n'
                                      '\n'},
 'fragment_pair_svc': {'svc/appender.py': '"""Append the errors fragment and the history '
                                          'fragment."""\n'
                                          'import sys\n'
                                          '\n'
                                          'FE, FH = "/tmp/_errors.md", "/tmp/_history.md"\n'
                                          'ERRORS = "/srv/memory/ERRORS.md"\n'
                                          '\n'
                                          '\n'
                                          'def append(fragment, target):\n'
                                          '    with open(target, "a", encoding="utf-8") as fh:\n'
                                          '        fh.write(open(fragment, '
                                          'encoding="utf-8").read())\n'
                                          '\n'
                                          '\n'
                                          'def main():\n'
                                          '    append(FE, ERRORS)\n'
                                          '    print("errors appended")\n'
                                          '    return 0\n'
                                          '\n'
                                          '\n'
                                          'if __name__ == "__main__":\n'
                                          '    sys.exit(main())\n'
                                          '\n'},
 'fragment_pair_used': {'appender.py': '"""Append both fragments, and say so."""\n'
                                       'import sys\n'
                                       '\n'
                                       'FE, FH = "/tmp/_errors.md", "/tmp/_history.md"\n'
                                       'ERRORS = "/srv/memory/ERRORS.md"\n'
                                       'HISTORY = "/srv/memory/SYSTEM_HISTORY.md"\n'
                                       '\n'
                                       '\n'
                                       'def append(fragment, target):\n'
                                       '    with open(target, "a", encoding="utf-8") as fh:\n'
                                       '        fh.write(open(fragment, encoding="utf-8").read())\n'
                                       '\n'
                                       '\n'
                                       'def main():\n'
                                       '    append(FE, ERRORS)\n'
                                       '    append(FH, HISTORY)\n'
                                       '    print("both appended")\n'
                                       '    return 0\n'
                                       '\n'
                                       '\n'
                                       'if __name__ == "__main__":\n'
                                       '    sys.exit(main())\n'
                                       '\n'},
 'fragment_pair_used_ren': {'appender.py': '"""Append both fragments, and say so."""\n'
                                           'import sys\n'
                                           '\n'
                                           'FE, FH = "/tmp/_errors.md", "/tmp/_history.md"\n'
                                           'ERRORS_v2 = "/srv/memory/ERRORS_v2.md"\n'
                                           'HISTORY = "/srv/memory/SYSTEM_HISTORY.md"\n'
                                           '\n'
                                           '\n'
                                           'def append(fragment, target):\n'
                                           '    with open(target, "a", encoding="utf-8") as fh:\n'
                                           '        fh.write(open(fragment, '
                                           'encoding="utf-8").read())\n'
                                           '\n'
                                           '\n'
                                           'def main():\n'
                                           '    append(FE, ERRORS_v2)\n'
                                           '    append(FH, HISTORY)\n'
                                           '    print("both appended")\n'
                                           '    return 0\n'
                                           '\n'
                                           '\n'
                                           'if __name__ == "__main__":\n'
                                           '    sys.exit(main())\n'
                                           '\n'},
 'fragment_pair_used_svc': {'svc/appender.py': '"""Append both fragments, and say so."""\n'
                                               'import sys\n'
                                               '\n'
                                               'FE, FH = "/tmp/_errors.md", "/tmp/_history.md"\n'
                                               'ERRORS = "/srv/memory/ERRORS.md"\n'
                                               'HISTORY = "/srv/memory/SYSTEM_HISTORY.md"\n'
                                               '\n'
                                               '\n'
                                               'def append(fragment, target):\n'
                                               '    with open(target, "a", encoding="utf-8") as '
                                               'fh:\n'
                                               '        fh.write(open(fragment, '
                                               'encoding="utf-8").read())\n'
                                               '\n'
                                               '\n'
                                               'def main():\n'
                                               '    append(FE, ERRORS)\n'
                                               '    append(FH, HISTORY)\n'
                                               '    print("both appended")\n'
                                               '    return 0\n'
                                               '\n'
                                               '\n'
                                               'if __name__ == "__main__":\n'
                                               '    sys.exit(main())\n'
                                               '\n'},
 'guard_after_normalise': {'appender.py': '"""Append a fragment, refusing one that does not end '
                                          'with a newline."""\n'
                                          'import sys\n'
                                          '\n'
                                          '\n'
                                          'def read_norm(path):\n'
                                          '    with open(path, encoding="utf-8") as fh:\n'
                                          '        return fh.read().replace(chr(13) + chr(10), '
                                          'chr(10)).replace(chr(13), chr(10))\n'
                                          '\n'
                                          '\n'
                                          'def main(path):\n'
                                          '    body = read_norm(path)\n'
                                          '    if not body.endswith(chr(10)):\n'
                                          '        print("REFUSING: " + path + " is not '
                                          'newline-terminated")\n'
                                          '        return 1\n'
                                          '    print("ok")\n'
                                          '    return 0\n'
                                          '\n'
                                          '\n'
                                          'if __name__ == "__main__":\n'
                                          '    sys.exit(main(sys.argv[1]))\n'
                                          '\n'},
 'guard_after_normalise_ren': {'appender.py': '"""Append a fragment, refusing one that does not '
                                              'end with a newline."""\n'
                                              'import sys\n'
                                              '\n'
                                              '\n'
                                              'def read_norm_v2(path):\n'
                                              '    with open(path, encoding="utf-8") as fh:\n'
                                              '        return fh.read().replace(chr(13) + chr(10), '
                                              'chr(10)).replace(chr(13), chr(10))\n'
                                              '\n'
                                              '\n'
                                              'def main(path):\n'
                                              '    body = read_norm_v2(path)\n'
                                              '    if not body.endswith(chr(10)):\n'
                                              '        print("REFUSING: " + path + " is not '
                                              'newline-terminated")\n'
                                              '        return 1\n'
                                              '    print("ok")\n'
                                              '    return 0\n'
                                              '\n'
                                              '\n'
                                              'if __name__ == "__main__":\n'
                                              '    sys.exit(main(sys.argv[1]))\n'
                                              '\n'},
 'guard_after_normalise_svc': {'svc/appender.py': '"""Append a fragment, refusing one that does '
                                                  'not end with a newline."""\n'
                                                  'import sys\n'
                                                  '\n'
                                                  '\n'
                                                  'def read_norm(path):\n'
                                                  '    with open(path, encoding="utf-8") as fh:\n'
                                                  '        return fh.read().replace(chr(13) + '
                                                  'chr(10), chr(10)).replace(chr(13), chr(10))\n'
                                                  '\n'
                                                  '\n'
                                                  'def main(path):\n'
                                                  '    body = read_norm(path)\n'
                                                  '    if not body.endswith(chr(10)):\n'
                                                  '        print("REFUSING: " + path + " is not '
                                                  'newline-terminated")\n'
                                                  '        return 1\n'
                                                  '    print("ok")\n'
                                                  '    return 0\n'
                                                  '\n'
                                                  '\n'
                                                  'if __name__ == "__main__":\n'
                                                  '    sys.exit(main(sys.argv[1]))\n'
                                                  '\n'},
 'home_paths_agree': {'paths.py': '"""One place decides where the delivery ledger lives."""\n'
                                  'from pathlib import Path\n'
                                  '\n'
                                  'LEDGER = Path.home() / ".local" / "state" / "notify" / '
                                  '"delivery.jsonl"\n'
                                  '\n',
                      'reader.py': '"""Count the rows the writer appended."""\n'
                                   'import json\n'
                                   '\n'
                                   'from paths import LEDGER\n'
                                   '\n'
                                   '\n'
                                   'def count():\n'
                                   '    if not LEDGER.exists():\n'
                                   '        return 0\n'
                                   '    with open(LEDGER, encoding="utf-8") as fh:\n'
                                   '        return sum(1 for line in fh if line.strip())\n'
                                   '\n',
                      'writer.py': '"""Append one delivery row."""\n'
                                   'import json\n'
                                   '\n'
                                   'from paths import LEDGER\n'
                                   '\n'
                                   '\n'
                                   'def append(row):\n'
                                   '    LEDGER.parent.mkdir(parents=True, exist_ok=True)\n'
                                   '    with open(LEDGER, "a") as fh:\n'
                                   '        fh.write(json.dumps(row) + chr(10))\n'
                                   '\n'},
 'home_paths_agree_ren': {'paths.py': '"""One place decides where the delivery ledger lives."""\n'
                                      'from pathlib import Path\n'
                                      '\n'
                                      'LEDGER = Path.home() / ".local" / "state" / "notify" / '
                                      '"delivery.jsonl"\n'
                                      '\n',
                          'reader.py': '"""Count the rows the writer appended."""\n'
                                       'import json\n'
                                       '\n'
                                       'from paths import LEDGER\n'
                                       '\n'
                                       '\n'
                                       'def count_v2():\n'
                                       '    if not LEDGER.exists():\n'
                                       '        return 0\n'
                                       '    with open(LEDGER, encoding="utf-8") as fh:\n'
                                       '        return sum(1 for line in fh if line.strip())\n'
                                       '\n',
                          'writer.py': '"""Append one delivery row."""\n'
                                       'import json\n'
                                       '\n'
                                       'from paths import LEDGER\n'
                                       '\n'
                                       '\n'
                                       'def append_v2(row):\n'
                                       '    LEDGER.parent.mkdir(parents=True, exist_ok=True)\n'
                                       '    with open(LEDGER, "a") as fh:\n'
                                       '        fh.write(json.dumps(row) + chr(10))\n'
                                       '\n'},
 'home_paths_agree_svc': {'svc/paths.py': '"""One place decides where the delivery ledger '
                                          'lives."""\n'
                                          'from pathlib import Path\n'
                                          '\n'
                                          'LEDGER = Path.home() / ".local" / "state" / "notify" / '
                                          '"delivery.jsonl"\n'
                                          '\n',
                          'svc/reader.py': '"""Count the rows the writer appended."""\n'
                                           'import json\n'
                                           '\n'
                                           'from paths import LEDGER\n'
                                           '\n'
                                           '\n'
                                           'def count():\n'
                                           '    if not LEDGER.exists():\n'
                                           '        return 0\n'
                                           '    with open(LEDGER, encoding="utf-8") as fh:\n'
                                           '        return sum(1 for line in fh if line.strip())\n'
                                           '\n',
                          'svc/writer.py': '"""Append one delivery row."""\n'
                                           'import json\n'
                                           '\n'
                                           'from paths import LEDGER\n'
                                           '\n'
                                           '\n'
                                           'def append(row):\n'
                                           '    LEDGER.parent.mkdir(parents=True, exist_ok=True)\n'
                                           '    with open(LEDGER, "a") as fh:\n'
                                           '        fh.write(json.dumps(row) + chr(10))\n'
                                           '\n'},
 'label_parser': {'labels.py': '"""Read the severity token an instrument puts at the head of its '
                               'own line."""\n'
                               'LABEL_MAX = 16\n'
                               '\n'
                               '\n'
                               'def label_of(line):\n'
                               '    s = (line or "").lstrip()\n'
                               '    if not s.startswith("["):\n'
                               '        return None\n'
                               '    j = s.find("]")\n'
                               '    if j < 2 or j > LABEL_MAX:\n'
                               '        return None\n'
                               '    tok = s[1:j]\n'
                               '    if not tok or not all(ch.isupper() or ch in "-_" for ch in '
                               'tok):\n'
                               '        return None\n'
                               '    return tok\n'
                               '\n'},
 'label_parser_ren': {'labels.py': '"""Read the severity token an instrument puts at the head of '
                                   'its own line."""\n'
                                   'LABEL_MAX_v2 = 16\n'
                                   '\n'
                                   '\n'
                                   'def label_of(line):\n'
                                   '    s = (line or "").lstrip()\n'
                                   '    if not s.startswith("["):\n'
                                   '        return None\n'
                                   '    j = s.find("]")\n'
                                   '    if j < 2 or j > LABEL_MAX_v2:\n'
                                   '        return None\n'
                                   '    tok = s[1:j]\n'
                                   '    if not tok or not all(ch.isupper() or ch in "-_" for ch in '
                                   'tok):\n'
                                   '        return None\n'
                                   '    return tok\n'
                                   '\n'},
 'label_parser_svc': {'svc/labels.py': '"""Read the severity token an instrument puts at the head '
                                       'of its own line."""\n'
                                       'LABEL_MAX = 16\n'
                                       '\n'
                                       '\n'
                                       'def label_of(line):\n'
                                       '    s = (line or "").lstrip()\n'
                                       '    if not s.startswith("["):\n'
                                       '        return None\n'
                                       '    j = s.find("]")\n'
                                       '    if j < 2 or j > LABEL_MAX:\n'
                                       '        return None\n'
                                       '    tok = s[1:j]\n'
                                       '    if not tok or not all(ch.isupper() or ch in "-_" for '
                                       'ch in tok):\n'
                                       '        return None\n'
                                       '    return tok\n'
                                       '\n'},
 'layout_shared_root': {'layout.py': '"""Resolve every ingest path from one root."""\n'
                                     'import os\n'
                                     '\n'
                                     'ROOT = os.path.join(os.path.expanduser("~"), ".local", '
                                     '"state", "ingest")\n'
                                     '\n'
                                     '\n'
                                     'def under(name):\n'
                                     '    return os.path.join(ROOT, name)\n'
                                     '\n',
                        'reader.py': '"""Read back the event lines the writer appended."""\n'
                                     'import json\n'
                                     'import os\n'
                                     '\n'
                                     'from layout import under\n'
                                     '\n'
                                     '\n'
                                     'def tail():\n'
                                     '    p = under("events.jsonl")\n'
                                     '    if not os.path.exists(p):\n'
                                     '        return []\n'
                                     '    with open(p, encoding="utf-8") as fh:\n'
                                     '        return [json.loads(line) for line in fh if '
                                     'line.strip()]\n'
                                     '\n',
                        'writer.py': '"""Append one event line."""\n'
                                     'import os\n'
                                     '\n'
                                     'from layout import under\n'
                                     '\n'
                                     '\n'
                                     'def append(line):\n'
                                     '    p = under("events.jsonl")\n'
                                     '    os.makedirs(os.path.dirname(p), exist_ok=True)\n'
                                     '    with open(p, "a", encoding="utf-8") as fh:\n'
                                     '        fh.write(line + chr(10))\n'
                                     '\n'},
 'layout_shared_root_ren': {'layout.py': '"""Resolve every ingest path from one root."""\n'
                                         'import os\n'
                                         '\n'
                                         'ROOT_v2 = os.path.join(os.path.expanduser("~"), '
                                         '".local", "state", "ingest")\n'
                                         '\n'
                                         '\n'
                                         'def under(name):\n'
                                         '    return os.path.join(ROOT_v2, name)\n'
                                         '\n',
                            'reader.py': '"""Read back the event lines the writer appended."""\n'
                                         'import json\n'
                                         'import os\n'
                                         '\n'
                                         'from layout import under\n'
                                         '\n'
                                         '\n'
                                         'def tail_v2():\n'
                                         '    p = under("events.jsonl")\n'
                                         '    if not os.path.exists(p):\n'
                                         '        return []\n'
                                         '    with open(p, encoding="utf-8") as fh:\n'
                                         '        return [json.loads(line) for line in fh if '
                                         'line.strip()]\n'
                                         '\n',
                            'writer.py': '"""Append one event line."""\n'
                                         'import os\n'
                                         '\n'
                                         'from layout import under\n'
                                         '\n'
                                         '\n'
                                         'def append_v2(line):\n'
                                         '    p = under("events.jsonl")\n'
                                         '    os.makedirs(os.path.dirname(p), exist_ok=True)\n'
                                         '    with open(p, "a", encoding="utf-8") as fh:\n'
                                         '        fh.write(line + chr(10))\n'
                                         '\n'},
 'layout_shared_root_svc': {'svc/layout.py': '"""Resolve every ingest path from one root."""\n'
                                             'import os\n'
                                             '\n'
                                             'ROOT = os.path.join(os.path.expanduser("~"), '
                                             '".local", "state", "ingest")\n'
                                             '\n'
                                             '\n'
                                             'def under(name):\n'
                                             '    return os.path.join(ROOT, name)\n'
                                             '\n',
                            'svc/reader.py': '"""Read back the event lines the writer '
                                             'appended."""\n'
                                             'import json\n'
                                             'import os\n'
                                             '\n'
                                             'from layout import under\n'
                                             '\n'
                                             '\n'
                                             'def tail():\n'
                                             '    p = under("events.jsonl")\n'
                                             '    if not os.path.exists(p):\n'
                                             '        return []\n'
                                             '    with open(p, encoding="utf-8") as fh:\n'
                                             '        return [json.loads(line) for line in fh if '
                                             'line.strip()]\n'
                                             '\n',
                            'svc/writer.py': '"""Append one event line."""\n'
                                             'import os\n'
                                             '\n'
                                             'from layout import under\n'
                                             '\n'
                                             '\n'
                                             'def append(line):\n'
                                             '    p = under("events.jsonl")\n'
                                             '    os.makedirs(os.path.dirname(p), exist_ok=True)\n'
                                             '    with open(p, "a", encoding="utf-8") as fh:\n'
                                             '        fh.write(line + chr(10))\n'
                                             '\n'},
 'leak_sentinel': {'NOTES.md': '# leak sentinel\n'
                               '\n'
                               'Runs from cron every 15 minutes. Its job is to notice when '
                               'somebody has written a planted\n'
                               'credential into a config file in this tree.\n'
                               '\n'
                               'When it fires it exits 3 and the cron wrapper mails the '
                               'operator.\n',
                   'crontab.txt': '*/15 * * * * /opt/leak_sentinel/sentinel.sh\n',
                   'sentinel.sh': '#!/bin/sh\n'
                                  '# Alert if a planted credential is present anywhere in this '
                                  'tree.\n'
                                  'DIR=$(dirname "$0")\n'
                                  'if grep -r "PLANTED_SECRET=" "$DIR"; then\n'
                                  '    echo "LEAK-DETECTED"\n'
                                  '    exit 3\n'
                                  'fi\n'
                                  'echo "LEAK-CLEAN"\n'
                                  'exit 0\n'},
 'leak_sentinel_ren': {'NOTES.md': '# leak sentinel\n'
                                   '\n'
                                   'Runs from cron every 15 minutes. Its job is to notice when '
                                   'somebody has written a planted\n'
                                   'credential into a config file in this tree.\n'
                                   '\n'
                                   'When it fires it exits 3 and the cron wrapper mails the '
                                   'operator.\n',
                       'crontab.txt': '*/15 * * * * /opt/leak_sentinel/sentinel.sh\n',
                       'sentinel.sh': '#!/bin/sh\n'
                                      '# Alert if a planted credential is present anywhere in this '
                                      'tree.\n'
                                      'DIR_v2=$(dirname "$0")\n'
                                      'if grep -r "PLANTED_SECRET=" "$DIR_v2"; then\n'
                                      '    echo "LEAK-DETECTED"\n'
                                      '    exit 3\n'
                                      'fi\n'
                                      'echo "LEAK-CLEAN"\n'
                                      'exit 0\n'},
 'leak_sentinel_svc': {'svc/NOTES.md': '# leak sentinel\n'
                                       '\n'
                                       'Runs from cron every 15 minutes. Its job is to notice when '
                                       'somebody has written a planted\n'
                                       'credential into a config file in this tree.\n'
                                       '\n'
                                       'When it fires it exits 3 and the cron wrapper mails the '
                                       'operator.\n',
                       'svc/crontab.txt': '*/15 * * * * /opt/leak_sentinel/sentinel.sh\n',
                       'svc/sentinel.sh': '#!/bin/sh\n'
                                          '# Alert if a planted credential is present anywhere in '
                                          'this tree.\n'
                                          'DIR=$(dirname "$0")\n'
                                          'if grep -r "PLANTED_SECRET=" "$DIR"; then\n'
                                          '    echo "LEAK-DETECTED"\n'
                                          '    exit 3\n'
                                          'fi\n'
                                          'echo "LEAK-CLEAN"\n'
                                          'exit 0\n'},
 'ledger_split': {'audit.py': '"""Append one audit row per run."""\n'
                              'import json\n'
                              'from pathlib import Path\n'
                              '\n'
                              '\n'
                              'def ledger():\n'
                              '    return Path.home() / ".local" / "state" / "app" / '
                              '"audit.jsonl"\n'
                              '\n'
                              '\n'
                              'def append(row):\n'
                              '    with open(ledger(), "a") as fh:\n'
                              '        fh.write(json.dumps(row) + chr(10))\n'
                              '\n'
                              '\n'
                              'if __name__ == "__main__":\n'
                              '    append({"event": "run"})\n'
                              '\n',
                  'audit.service': '[Unit]\n'
                                   'Description=audit appender\n'
                                   '\n'
                                   '[Service]\n'
                                   'Type=oneshot\n'
                                   'User=deploy\n'
                                   'ExecStart=/usr/bin/python3 /opt/app/audit.py\n'
                                   '\n',
                  'dashboard.py': '"""Count audit rows for the status page."""\n'
                                  'import json\n'
                                  '\n'
                                  'LEDGER = "/srv/app/audit.jsonl"\n'
                                  '\n'
                                  '\n'
                                  'def count():\n'
                                  '    with open(LEDGER, encoding="utf-8") as fh:\n'
                                  '        return sum(1 for line in fh if line.strip())\n'
                                  '\n'},
 'ledger_split_ren': {'audit.py': '"""Append one audit row per run."""\n'
                                  'import json\n'
                                  'from pathlib import Path\n'
                                  '\n'
                                  '\n'
                                  'def ledger_v2():\n'
                                  '    return Path.home() / ".local" / "state" / "app" / '
                                  '"audit.jsonl"\n'
                                  '\n'
                                  '\n'
                                  'def append_v2(row):\n'
                                  '    with open(ledger_v2(), "a") as fh:\n'
                                  '        fh.write(json.dumps(row) + chr(10))\n'
                                  '\n'
                                  '\n'
                                  'if __name__ == "__main__":\n'
                                  '    append_v2({"event": "run"})\n'
                                  '\n',
                      'audit.service': '[Unit]\n'
                                       'Description=audit appender\n'
                                       '\n'
                                       '[Service]\n'
                                       'Type=oneshot\n'
                                       'User=deploy\n'
                                       'ExecStart=/usr/bin/python3 /opt/app/audit.py\n'
                                       '\n',
                      'dashboard.py': '"""Count audit rows for the status page."""\n'
                                      'import json\n'
                                      '\n'
                                      'LEDGER_v2 = "/srv/app/audit.jsonl"\n'
                                      '\n'
                                      '\n'
                                      'def count_v2():\n'
                                      '    with open(LEDGER_v2, encoding="utf-8") as fh:\n'
                                      '        return sum(1 for line in fh if line.strip())\n'
                                      '\n'},
 'ledger_split_svc': {'svc/audit.py': '"""Append one audit row per run."""\n'
                                      'import json\n'
                                      'from pathlib import Path\n'
                                      '\n'
                                      '\n'
                                      'def ledger():\n'
                                      '    return Path.home() / ".local" / "state" / "app" / '
                                      '"audit.jsonl"\n'
                                      '\n'
                                      '\n'
                                      'def append(row):\n'
                                      '    with open(ledger(), "a") as fh:\n'
                                      '        fh.write(json.dumps(row) + chr(10))\n'
                                      '\n'
                                      '\n'
                                      'if __name__ == "__main__":\n'
                                      '    append({"event": "run"})\n'
                                      '\n',
                      'svc/audit.service': '[Unit]\n'
                                           'Description=audit appender\n'
                                           '\n'
                                           '[Service]\n'
                                           'Type=oneshot\n'
                                           'User=deploy\n'
                                           'ExecStart=/usr/bin/python3 /opt/app/audit.py\n'
                                           '\n',
                      'svc/dashboard.py': '"""Count audit rows for the status page."""\n'
                                          'import json\n'
                                          '\n'
                                          'LEDGER = "/srv/app/audit.jsonl"\n'
                                          '\n'
                                          '\n'
                                          'def count():\n'
                                          '    with open(LEDGER, encoding="utf-8") as fh:\n'
                                          '        return sum(1 for line in fh if line.strip())\n'
                                          '\n'},
 'masked_pipeline': {'check_headings.sh': '#!/bin/sh\n'
                                          'set -e\n'
                                          'ERRORS=/srv/memory/ERRORS.md\n'
                                          'echo "headings:"\n'
                                          'grep -o "^### " "$ERRORS" | tail -n 3\n'
                                          'echo "done"\n'
                                          '\n'},
 'masked_pipeline_svc': {'svc/check_headings.sh': '#!/bin/sh\n'
                                                  'set -e\n'
                                                  'ERRORS=/srv/memory/ERRORS.md\n'
                                                  'echo "headings:"\n'
                                                  'grep -o "^### " "$ERRORS" | tail -n 3\n'
                                                  'echo "done"\n'
                                                  '\n'},
 'mem_guard': {'check_mem.py': '"""Verify memory pressure stays under the configured limit. Exit 3 '
                               'means over limit."""\n'
                               'import json\n'
                               'import sys\n'
                               '\n'
                               '\n'
                               "def check(path='limits.json'):\n"
                               '    with open(path) as fh:\n'
                               "        limit = json.load(fh)['mem_pct']\n"
                               "    total, used = _meminfo('/proc/meminfo')\n"
                               '    pct = used / total * 100\n'
                               '    if pct > limit:\n'
                               "        print('MEM-OVER-LIMIT pct=%.1f limit=%s' % (pct, limit))\n"
                               '        return 3\n'
                               "    print('mem ok pct=%.1f limit=%s' % (pct, limit))\n"
                               '    return 0\n'
                               '\n'
                               '\n'
                               'def _meminfo(path):\n'
                               '    vals = {}\n'
                               '    with open(path) as fh:\n'
                               '        for line in fh:\n'
                               "            k, _, v = line.partition(':')\n"
                               '            vals[k.strip()] = int(v.split()[0])\n'
                               "    total = vals['MemTotal']\n"
                               "    return total, total - vals['MemAvailable']\n"
                               '\n'
                               '\n'
                               "if __name__ == '__main__':\n"
                               '    sys.exit(check(*sys.argv[1:]))\n',
               'ledger.py': '"""Append delivery rows and read them back. Writer and reader agree '
                            'on one absolute path."""\n'
                            'import json\n'
                            '\n'
                            "LEDGER = '/opt/mem_guard/ledger.jsonl'\n"
                            '\n'
                            '\n'
                            'def append(row):\n'
                            "    with open(LEDGER, 'a') as fh:\n"
                            '        fh.write(json.dumps(row) + chr(10))\n'
                            '\n'
                            '\n'
                            'def read_all():\n'
                            "    with open(LEDGER, encoding='utf-8') as fh:\n"
                            '        return [json.loads(x) for x in fh if x.strip()]\n',
               'limits.json': '{"mem_pct": 92}',
               'run_mem_guard.sh': '#!/bin/sh\n'
                                   '# Cron calls this. The exit status is the only signal that '
                                   'reaches the operator.\n'
                                   'python3 check_mem.py limits.json\n'
                                   'status=$?\n'
                                   'if [ "$status" -ne 0 ]; then\n'
                                   '    echo "MEM-GUARD FAILED status=$status"\n'
                                   '    exit $status\n'
                                   'fi\n'
                                   'echo "MEM-GUARD OK"\n'
                                   'exit 0\n',
               'test_check_mem.py': '"""Calls the real check() against a fixture limits file; '
                                    'nothing under test is replaced."""\n'
                                    'import json\n'
                                    'import os\n'
                                    'import tempfile\n'
                                    '\n'
                                    'import check_mem\n'
                                    '\n'
                                    '\n'
                                    'def test_over_limit_returns_three(monkeypatch):\n'
                                    '    d = tempfile.mkdtemp()\n'
                                    "    p = os.path.join(d, 'limits.json')\n"
                                    "    with open(p, 'w') as fh:\n"
                                    "        json.dump({'mem_pct': 0}, fh)\n"
                                    "    monkeypatch.setattr(check_mem, '_meminfo', lambda path: "
                                    '(100, 50))\n'
                                    '    assert check_mem.check(p) == 3\n'
                                    '\n'
                                    '\n'
                                    'def test_under_limit_returns_zero(monkeypatch):\n'
                                    '    d = tempfile.mkdtemp()\n'
                                    "    p = os.path.join(d, 'limits.json')\n"
                                    "    with open(p, 'w') as fh:\n"
                                    "        json.dump({'mem_pct': 92}, fh)\n"
                                    "    monkeypatch.setattr(check_mem, '_meminfo', lambda path: "
                                    '(100, 10))\n'
                                    '    assert check_mem.check(p) == 0\n'},
 'mem_guard_ren': {'check_mem.py': '"""Verify memory pressure stays under the configured limit. '
                                   'Exit 3 means over limit."""\n'
                                   'import json\n'
                                   'import sys\n'
                                   '\n'
                                   '\n'
                                   "def check_v2(path='limits.json'):\n"
                                   '    with open(path) as fh:\n'
                                   "        limit = json.load(fh)['mem_pct']\n"
                                   "    total, used = _meminfo_v2('/proc/meminfo')\n"
                                   '    pct = used / total * 100\n'
                                   '    if pct > limit:\n'
                                   "        print('MEM-OVER-LIMIT pct=%.1f limit=%s' % (pct, "
                                   'limit))\n'
                                   '        return 3\n'
                                   "    print('mem ok pct=%.1f limit=%s' % (pct, limit))\n"
                                   '    return 0\n'
                                   '\n'
                                   '\n'
                                   'def _meminfo_v2(path):\n'
                                   '    vals = {}\n'
                                   '    with open(path) as fh:\n'
                                   '        for line in fh:\n'
                                   "            k, _, v = line.partition(':')\n"
                                   '            vals[k.strip()] = int(v.split()[0])\n'
                                   "    total = vals['MemTotal']\n"
                                   "    return total, total - vals['MemAvailable']\n"
                                   '\n'
                                   '\n'
                                   "if __name__ == '__main__':\n"
                                   '    sys.exit(check_v2(*sys.argv[1:]))\n',
                   'ledger.py': '"""Append delivery rows and read them back. Writer and reader '
                                'agree on one absolute path."""\n'
                                'import json\n'
                                '\n'
                                "LEDGER_v2 = '/opt/mem_guard/ledger.jsonl'\n"
                                '\n'
                                '\n'
                                'def append_v2(row):\n'
                                "    with open(LEDGER_v2, 'a') as fh:\n"
                                '        fh.write(json.dumps(row) + chr(10))\n'
                                '\n'
                                '\n'
                                'def read_all_v2():\n'
                                "    with open(LEDGER_v2, encoding='utf-8') as fh:\n"
                                '        return [json.loads(x) for x in fh if x.strip()]\n',
                   'limits.json': '{"mem_pct": 92}',
                   'run_mem_guard.sh': '#!/bin/sh\n'
                                       '# Cron calls this. The exit status is the only signal that '
                                       'reaches the operator.\n'
                                       'python3 check_mem.py limits.json\n'
                                       'status=$?\n'
                                       'if [ "$status" -ne 0 ]; then\n'
                                       '    echo "MEM-GUARD FAILED status=$status"\n'
                                       '    exit $status\n'
                                       'fi\n'
                                       'echo "MEM-GUARD OK"\n'
                                       'exit 0\n',
                   'test_check_mem.py': '"""Calls the real check_v2() against a fixture limits '
                                        'file; nothing under test is replaced."""\n'
                                        'import json\n'
                                        'import os\n'
                                        'import tempfile\n'
                                        '\n'
                                        'import check_mem\n'
                                        '\n'
                                        '\n'
                                        'def test_over_limit_returns_three_v2(monkeypatch):\n'
                                        '    d = tempfile.mkdtemp()\n'
                                        "    p = os.path.join(d, 'limits.json')\n"
                                        "    with open(p, 'w') as fh:\n"
                                        "        json.dump({'mem_pct': 0}, fh)\n"
                                        "    monkeypatch.setattr(check_mem, '_meminfo_v2', lambda "
                                        'path: (100, 50))\n'
                                        '    assert check_mem.check_v2(p) == 3\n'
                                        '\n'
                                        '\n'
                                        'def test_under_limit_returns_zero_v2(monkeypatch):\n'
                                        '    d = tempfile.mkdtemp()\n'
                                        "    p = os.path.join(d, 'limits.json')\n"
                                        "    with open(p, 'w') as fh:\n"
                                        "        json.dump({'mem_pct': 92}, fh)\n"
                                        "    monkeypatch.setattr(check_mem, '_meminfo_v2', lambda "
                                        'path: (100, 10))\n'
                                        '    assert check_mem.check_v2(p) == 0\n'},
 'mem_guard_svc': {'svc/check_mem.py': '"""Verify memory pressure stays under the configured '
                                       'limit. Exit 3 means over limit."""\n'
                                       'import json\n'
                                       'import sys\n'
                                       '\n'
                                       '\n'
                                       "def check(path='limits.json'):\n"
                                       '    with open(path) as fh:\n'
                                       "        limit = json.load(fh)['mem_pct']\n"
                                       "    total, used = _meminfo('/proc/meminfo')\n"
                                       '    pct = used / total * 100\n'
                                       '    if pct > limit:\n'
                                       "        print('MEM-OVER-LIMIT pct=%.1f limit=%s' % (pct, "
                                       'limit))\n'
                                       '        return 3\n'
                                       "    print('mem ok pct=%.1f limit=%s' % (pct, limit))\n"
                                       '    return 0\n'
                                       '\n'
                                       '\n'
                                       'def _meminfo(path):\n'
                                       '    vals = {}\n'
                                       '    with open(path) as fh:\n'
                                       '        for line in fh:\n'
                                       "            k, _, v = line.partition(':')\n"
                                       '            vals[k.strip()] = int(v.split()[0])\n'
                                       "    total = vals['MemTotal']\n"
                                       "    return total, total - vals['MemAvailable']\n"
                                       '\n'
                                       '\n'
                                       "if __name__ == '__main__':\n"
                                       '    sys.exit(check(*sys.argv[1:]))\n',
                   'svc/ledger.py': '"""Append delivery rows and read them back. Writer and reader '
                                    'agree on one absolute path."""\n'
                                    'import json\n'
                                    '\n'
                                    "LEDGER = '/opt/mem_guard/ledger.jsonl'\n"
                                    '\n'
                                    '\n'
                                    'def append(row):\n'
                                    "    with open(LEDGER, 'a') as fh:\n"
                                    '        fh.write(json.dumps(row) + chr(10))\n'
                                    '\n'
                                    '\n'
                                    'def read_all():\n'
                                    "    with open(LEDGER, encoding='utf-8') as fh:\n"
                                    '        return [json.loads(x) for x in fh if x.strip()]\n',
                   'svc/limits.json': '{"mem_pct": 92}',
                   'svc/run_mem_guard.sh': '#!/bin/sh\n'
                                           '# Cron calls this. The exit status is the only signal '
                                           'that reaches the operator.\n'
                                           'python3 check_mem.py limits.json\n'
                                           'status=$?\n'
                                           'if [ "$status" -ne 0 ]; then\n'
                                           '    echo "MEM-GUARD FAILED status=$status"\n'
                                           '    exit $status\n'
                                           'fi\n'
                                           'echo "MEM-GUARD OK"\n'
                                           'exit 0\n',
                   'svc/test_check_mem.py': '"""Calls the real check() against a fixture limits '
                                            'file; nothing under test is replaced."""\n'
                                            'import json\n'
                                            'import os\n'
                                            'import tempfile\n'
                                            '\n'
                                            'import check_mem\n'
                                            '\n'
                                            '\n'
                                            'def test_over_limit_returns_three(monkeypatch):\n'
                                            '    d = tempfile.mkdtemp()\n'
                                            "    p = os.path.join(d, 'limits.json')\n"
                                            "    with open(p, 'w') as fh:\n"
                                            "        json.dump({'mem_pct': 0}, fh)\n"
                                            "    monkeypatch.setattr(check_mem, '_meminfo', lambda "
                                            'path: (100, 50))\n'
                                            '    assert check_mem.check(p) == 3\n'
                                            '\n'
                                            '\n'
                                            'def test_under_limit_returns_zero(monkeypatch):\n'
                                            '    d = tempfile.mkdtemp()\n'
                                            "    p = os.path.join(d, 'limits.json')\n"
                                            "    with open(p, 'w') as fh:\n"
                                            "        json.dump({'mem_pct': 92}, fh)\n"
                                            "    monkeypatch.setattr(check_mem, '_meminfo', lambda "
                                            'path: (100, 10))\n'
                                            '    assert check_mem.check(p) == 0\n'},
 'memory_append': {'appender.py': '"""Append one entry to a memory file and replicate it to the '
                                  'peers."""\n'
                                  'import os\n'
                                  'import subprocess\n'
                                  'import sys\n'
                                  '\n'
                                  'MEMORY = "/srv/memory/ERRORS.md"\n'
                                  'BACKUP = "/opt/tools/memory_backup.sh"\n'
                                  '\n'
                                  '\n'
                                  'def append(fragment):\n'
                                  '    if not os.path.exists(fragment):\n'
                                  '        print("missing fragment")\n'
                                  '        return 1\n'
                                  '    with open(MEMORY, "a", encoding="utf-8") as fh:\n'
                                  '        fh.write(open(fragment, encoding="utf-8").read())\n'
                                  '    for args in ([BACKUP], [BACKUP, "--verify"]):\n'
                                  '        p = subprocess.run(args)\n'
                                  '        print("rc=%d %s" % (p.returncode, " ".join(args)))\n'
                                  '    return 0\n'
                                  '\n'
                                  '\n'
                                  'if __name__ == "__main__":\n'
                                  '    sys.exit(append(sys.argv[1]))\n'
                                  '\n'},
 'memory_append_ren': {'appender.py': '"""Append one entry to a memory file and replicate it to '
                                      'the peers."""\n'
                                      'import os\n'
                                      'import subprocess\n'
                                      'import sys\n'
                                      '\n'
                                      'MEMORY_v2 = "/srv/memory/ERRORS.md"\n'
                                      'BACKUP_v2 = "/opt/tools/memory_backup.sh"\n'
                                      '\n'
                                      '\n'
                                      'def append_v2(fragment):\n'
                                      '    if not os.path.exists(fragment):\n'
                                      '        print("missing fragment")\n'
                                      '        return 1\n'
                                      '    with open(MEMORY_v2, "a", encoding="utf-8") as fh:\n'
                                      '        fh.write(open(fragment, encoding="utf-8").read())\n'
                                      '    for args in ([BACKUP_v2], [BACKUP_v2, "--verify"]):\n'
                                      '        p = subprocess.run(args)\n'
                                      '        print("rc=%d %s" % (p.returncode, " ".join(args)))\n'
                                      '    return 0\n'
                                      '\n'
                                      '\n'
                                      'if __name__ == "__main__":\n'
                                      '    sys.exit(append_v2(sys.argv[1]))\n'
                                      '\n'},
 'memory_append_svc': {'svc/appender.py': '"""Append one entry to a memory file and replicate it '
                                          'to the peers."""\n'
                                          'import os\n'
                                          'import subprocess\n'
                                          'import sys\n'
                                          '\n'
                                          'MEMORY = "/srv/memory/ERRORS.md"\n'
                                          'BACKUP = "/opt/tools/memory_backup.sh"\n'
                                          '\n'
                                          '\n'
                                          'def append(fragment):\n'
                                          '    if not os.path.exists(fragment):\n'
                                          '        print("missing fragment")\n'
                                          '        return 1\n'
                                          '    with open(MEMORY, "a", encoding="utf-8") as fh:\n'
                                          '        fh.write(open(fragment, '
                                          'encoding="utf-8").read())\n'
                                          '    for args in ([BACKUP], [BACKUP, "--verify"]):\n'
                                          '        p = subprocess.run(args)\n'
                                          '        print("rc=%d %s" % (p.returncode, " '
                                          '".join(args)))\n'
                                          '    return 0\n'
                                          '\n'
                                          '\n'
                                          'if __name__ == "__main__":\n'
                                          '    sys.exit(append(sys.argv[1]))\n'
                                          '\n'},
 'mock_external': {'fetch.py': '"""Read a URL body as text."""\n'
                               'import urllib.request\n'
                               '\n'
                               '\n'
                               'def body(url, timeout=5):\n'
                               '    with urllib.request.urlopen(url, timeout=timeout) as fh:\n'
                               '        return fh.read().decode("utf-8")\n'
                               '\n',
                   'test_fetch.py': '"""fetch.body is exercised for real; only the network '
                                    'dependency is replaced."""\n'
                                    'from unittest import mock\n'
                                    '\n'
                                    'import fetch\n'
                                    '\n'
                                    '\n'
                                    'def test_body_decodes_utf8():\n'
                                    '    with mock.patch("urllib.request.urlopen") as urlopen:\n'
                                    '        handle = urlopen.return_value.__enter__.return_value\n'
                                    '        handle.read.return_value = '
                                    '"h\\u00e9llo".encode("utf-8")\n'
                                    '        assert fetch.body("http://example.invalid") == '
                                    '"h\\u00e9llo"\n'
                                    '\n'},
 'mock_external_ren': {'fetch.py': '"""Read a URL body_v2 as text."""\n'
                                   'import urllib.request\n'
                                   '\n'
                                   '\n'
                                   'def body_v2(url, timeout=5):\n'
                                   '    with urllib.request.urlopen(url, timeout=timeout) as fh:\n'
                                   '        return fh.read().decode("utf-8")\n'
                                   '\n',
                       'test_fetch.py': '"""fetch.body_v2 is exercised for real; only the network '
                                        'dependency is replaced."""\n'
                                        'from unittest import mock\n'
                                        '\n'
                                        'import fetch\n'
                                        '\n'
                                        '\n'
                                        'def test_body_decodes_utf8_v2():\n'
                                        '    with mock.patch("urllib.request.urlopen") as '
                                        'urlopen:\n'
                                        '        handle = '
                                        'urlopen.return_value.__enter__.return_value\n'
                                        '        handle.read.return_value = '
                                        '"h\\u00e9llo".encode("utf-8")\n'
                                        '        assert fetch.body_v2("http://example.invalid") == '
                                        '"h\\u00e9llo"\n'
                                        '\n'},
 'mock_external_svc': {'svc/fetch.py': '"""Read a URL body as text."""\n'
                                       'import urllib.request\n'
                                       '\n'
                                       '\n'
                                       'def body(url, timeout=5):\n'
                                       '    with urllib.request.urlopen(url, timeout=timeout) as '
                                       'fh:\n'
                                       '        return fh.read().decode("utf-8")\n'
                                       '\n',
                       'svc/test_fetch.py': '"""fetch.body is exercised for real; only the network '
                                            'dependency is replaced."""\n'
                                            'from unittest import mock\n'
                                            '\n'
                                            'import fetch\n'
                                            '\n'
                                            '\n'
                                            'def test_body_decodes_utf8():\n'
                                            '    with mock.patch("urllib.request.urlopen") as '
                                            'urlopen:\n'
                                            '        handle = '
                                            'urlopen.return_value.__enter__.return_value\n'
                                            '        handle.read.return_value = '
                                            '"h\\u00e9llo".encode("utf-8")\n'
                                            '        assert fetch.body("http://example.invalid") '
                                            '== "h\\u00e9llo"\n'
                                            '\n'},
 'mock_self_assert': {'sender.py': '"""Deliver one message through the transport the caller passes '
                                   'in."""\n'
                                   '\n'
                                   '\n'
                                   'def deliver(transport, message):\n'
                                   '    return transport.send(message)\n'
                                   '\n',
                      'test_sender.py': '"""Tests for sender.deliver."""\n'
                                        'from unittest import mock\n'
                                        '\n'
                                        'import sender\n'
                                        '\n'
                                        '\n'
                                        'def test_deliver_sends():\n'
                                        '    transport = mock.Mock()\n'
                                        '    sender.deliver = mock.Mock(return_value=0)\n'
                                        '    sender.deliver(transport, "hi")\n'
                                        '    sender.deliver.assert_called_once_with(transport, '
                                        '"hi")\n'
                                        '\n'},
 'mock_self_assert_ren': {'sender.py': '"""Deliver one message through the transport the caller '
                                       'passes in."""\n'
                                       '\n'
                                       '\n'
                                       'def deliver(transport, message):\n'
                                       '    return transport.send(message)\n'
                                       '\n',
                          'test_sender.py': '"""Tests for sender.deliver."""\n'
                                            'from unittest import mock\n'
                                            '\n'
                                            'import sender\n'
                                            '\n'
                                            '\n'
                                            'def test_deliver_sends_v2():\n'
                                            '    transport = mock.Mock()\n'
                                            '    sender.deliver = mock.Mock(return_value=0)\n'
                                            '    sender.deliver(transport, "hi")\n'
                                            '    sender.deliver.assert_called_once_with(transport, '
                                            '"hi")\n'
                                            '\n'},
 'mock_self_assert_svc': {'svc/sender.py': '"""Deliver one message through the transport the '
                                           'caller passes in."""\n'
                                           '\n'
                                           '\n'
                                           'def deliver(transport, message):\n'
                                           '    return transport.send(message)\n'
                                           '\n',
                          'svc/test_sender.py': '"""Tests for sender.deliver."""\n'
                                                'from unittest import mock\n'
                                                '\n'
                                                'import sender\n'
                                                '\n'
                                                '\n'
                                                'def test_deliver_sends():\n'
                                                '    transport = mock.Mock()\n'
                                                '    sender.deliver = mock.Mock(return_value=0)\n'
                                                '    sender.deliver(transport, "hi")\n'
                                                '    '
                                                'sender.deliver.assert_called_once_with(transport, '
                                                '"hi")\n'
                                                '\n'},
 'mock_subject': {'report.py': '"""Send the daily report through the configured command."""\n'
                               'import os\n'
                               'import subprocess\n'
                               '\n'
                               'DEFAULT = "report.py --send --strict"\n'
                               '\n'
                               '\n'
                               'def send():\n'
                               '    cmd = os.environ.get("REPORT_CMD", DEFAULT)\n'
                               '    return subprocess.call(cmd, shell=True)\n'
                               '\n',
                  'test_report.py': '"""Tests for report.send."""\n'
                                    'import os\n'
                                    '\n'
                                    'os.environ["REPORT_CMD"] = "true"\n'
                                    'import report\n'
                                    '\n'
                                    '\n'
                                    'def test_send_returns_zero():\n'
                                    '    assert report.send() == 0\n'
                                    '\n'},
 'mock_subject_ren': {'report.py': '"""Send the daily report through the configured command."""\n'
                                   'import os\n'
                                   'import subprocess\n'
                                   '\n'
                                   'DEFAULT_v2 = "report.py --send_v2 --strict"\n'
                                   '\n'
                                   '\n'
                                   'def send_v2():\n'
                                   '    cmd = os.environ.get("REPORT_CMD", DEFAULT_v2)\n'
                                   '    return subprocess.call(cmd, shell=True)\n'
                                   '\n',
                      'test_report.py': '"""Tests for report.send_v2."""\n'
                                        'import os\n'
                                        '\n'
                                        'os.environ["REPORT_CMD"] = "true"\n'
                                        'import report\n'
                                        '\n'
                                        '\n'
                                        'def test_send_returns_zero_v2():\n'
                                        '    assert report.send_v2() == 0\n'
                                        '\n'},
 'mock_subject_svc': {'svc/report.py': '"""Send the daily report through the configured '
                                       'command."""\n'
                                       'import os\n'
                                       'import subprocess\n'
                                       '\n'
                                       'DEFAULT = "report.py --send --strict"\n'
                                       '\n'
                                       '\n'
                                       'def send():\n'
                                       '    cmd = os.environ.get("REPORT_CMD", DEFAULT)\n'
                                       '    return subprocess.call(cmd, shell=True)\n'
                                       '\n',
                      'svc/test_report.py': '"""Tests for report.send."""\n'
                                            'import os\n'
                                            '\n'
                                            'os.environ["REPORT_CMD"] = "true"\n'
                                            'import report\n'
                                            '\n'
                                            '\n'
                                            'def test_send_returns_zero():\n'
                                            '    assert report.send() == 0\n'
                                            '\n'},
 'normalise_then_test': {'appender.py': '"""Append a fragment once the carriage-return check has '
                                        'passed."""\n'
                                        'import sys\n'
                                        '\n'
                                        '\n'
                                        'def read_norm(path):\n'
                                        '    with open(path, encoding="utf-8") as fh:\n'
                                        '        return fh.read().replace(chr(13) + chr(10), '
                                        'chr(10)).replace(chr(13), chr(10))\n'
                                        '\n'
                                        '\n'
                                        'def main(path):\n'
                                        '    body = read_norm(path)\n'
                                        '    if chr(13) in body:\n'
                                        '        print("REFUSING: carriage returns in " + path)\n'
                                        '        return 1\n'
                                        '    print("ok")\n'
                                        '    return 0\n'
                                        '\n'
                                        '\n'
                                        'if __name__ == "__main__":\n'
                                        '    sys.exit(main(sys.argv[1]))\n'
                                        '\n'},
 'normalise_then_test_ren': {'appender.py': '"""Append a fragment once the carriage-return check '
                                            'has passed."""\n'
                                            'import sys\n'
                                            '\n'
                                            '\n'
                                            'def read_norm_v2(path):\n'
                                            '    with open(path, encoding="utf-8") as fh:\n'
                                            '        return fh.read().replace(chr(13) + chr(10), '
                                            'chr(10)).replace(chr(13), chr(10))\n'
                                            '\n'
                                            '\n'
                                            'def main(path):\n'
                                            '    body = read_norm_v2(path)\n'
                                            '    if chr(13) in body:\n'
                                            '        print("REFUSING: carriage returns in " + '
                                            'path)\n'
                                            '        return 1\n'
                                            '    print("ok")\n'
                                            '    return 0\n'
                                            '\n'
                                            '\n'
                                            'if __name__ == "__main__":\n'
                                            '    sys.exit(main(sys.argv[1]))\n'
                                            '\n'},
 'normalise_then_test_svc': {'svc/appender.py': '"""Append a fragment once the carriage-return '
                                                'check has passed."""\n'
                                                'import sys\n'
                                                '\n'
                                                '\n'
                                                'def read_norm(path):\n'
                                                '    with open(path, encoding="utf-8") as fh:\n'
                                                '        return fh.read().replace(chr(13) + '
                                                'chr(10), chr(10)).replace(chr(13), chr(10))\n'
                                                '\n'
                                                '\n'
                                                'def main(path):\n'
                                                '    body = read_norm(path)\n'
                                                '    if chr(13) in body:\n'
                                                '        print("REFUSING: carriage returns in " + '
                                                'path)\n'
                                                '        return 1\n'
                                                '    print("ok")\n'
                                                '    return 0\n'
                                                '\n'
                                                '\n'
                                                'if __name__ == "__main__":\n'
                                                '    sys.exit(main(sys.argv[1]))\n'
                                                '\n'},
 'notify_path': {'estate-notify.service': '[Unit]\n'
                                          'Description=estate alert sender\n'
                                          '\n'
                                          '[Service]\n'
                                          'Type=oneshot\n'
                                          'User=root\n'
                                          'ExecStart=/usr/bin/python3 /opt/estate/notify.py\n',
                 'notify.py': '"""Send one alert, then append a row to the delivery ledger.\n'
                              '\n'
                              "The ledger lives in the operator's home directory, next to the "
                              'other state files.\n'
                              '"""\n'
                              'import json\n'
                              'import os\n'
                              '\n'
                              '\n'
                              'def ledger_path():\n'
                              '    return os.path.join(os.path.expanduser(chr(126)), '
                              "'.omni_brain', 'notify_delivery.jsonl')\n"
                              '\n'
                              '\n'
                              'def notify(title, body):\n'
                              "    ok = os.system('logger -t estate-notify ' + title) == 0\n"
                              "    row = {'title': title, 'body': body, 'sent': ok}\n"
                              "    with open(ledger_path(), 'a') as fh:\n"
                              '        fh.write(json.dumps(row) + chr(10))\n'
                              '    return 0 if ok else 1\n'
                              '\n'
                              '\n'
                              "if __name__ == '__main__':\n"
                              "    raise SystemExit(notify('disk full', 'root at 98 percent'))\n",
                 'reader.py': '"""Report how many notifications were delivered today."""\n'
                              'import json\n'
                              '\n'
                              "LEDGER = '/home/zixen15/.omni_brain/notify_delivery.jsonl'\n"
                              '\n'
                              '\n'
                              'def count_rows(rows=None):\n'
                              '    if rows is None:\n'
                              "        with open(LEDGER, encoding='utf-8') as fh:\n"
                              '            rows = [json.loads(x) for x in fh if x.strip()]\n'
                              '    return len(rows)\n'},
 'notify_path_ren': {'estate-notify.service': '[Unit]\n'
                                              'Description=estate alert sender\n'
                                              '\n'
                                              '[Service]\n'
                                              'Type=oneshot\n'
                                              'User=root\n'
                                              'ExecStart=/usr/bin/python3 '
                                              '/opt/estate/notify_v2.py\n',
                     'notify.py': '"""Send one alert, then append a row to the delivery ledger.\n'
                                  '\n'
                                  "The ledger lives in the operator's home directory, next to the "
                                  'other state files.\n'
                                  '"""\n'
                                  'import json\n'
                                  'import os\n'
                                  '\n'
                                  '\n'
                                  'def ledger_path_v2():\n'
                                  '    return os.path.join(os.path.expanduser(chr(126)), '
                                  "'.omni_brain', 'notify_delivery.jsonl')\n"
                                  '\n'
                                  '\n'
                                  'def notify_v2(title, body):\n'
                                  "    ok = os.system('logger -t estate-notify_v2 ' + title) == 0\n"
                                  "    row = {'title': title, 'body': body, 'sent': ok}\n"
                                  "    with open(ledger_path_v2(), 'a') as fh:\n"
                                  '        fh.write(json.dumps(row) + chr(10))\n'
                                  '    return 0 if ok else 1\n'
                                  '\n'
                                  '\n'
                                  "if __name__ == '__main__':\n"
                                  "    raise SystemExit(notify_v2('disk full', 'root at 98 "
                                  "percent'))\n",
                     'reader.py': '"""Report how many notifications were delivered today."""\n'
                                  'import json\n'
                                  '\n'
                                  "LEDGER_v2 = '/home/zixen15/.omni_brain/notify_delivery.jsonl'\n"
                                  '\n'
                                  '\n'
                                  'def count_rows_v2(rows=None):\n'
                                  '    if rows is None:\n'
                                  "        with open(LEDGER_v2, encoding='utf-8') as fh:\n"
                                  '            rows = [json.loads(x) for x in fh if x.strip()]\n'
                                  '    return len(rows)\n'},
 'notify_path_svc': {'svc/estate-notify.service': '[Unit]\n'
                                                  'Description=estate alert sender\n'
                                                  '\n'
                                                  '[Service]\n'
                                                  'Type=oneshot\n'
                                                  'User=root\n'
                                                  'ExecStart=/usr/bin/python3 '
                                                  '/opt/estate/notify.py\n',
                     'svc/notify.py': '"""Send one alert, then append a row to the delivery '
                                      'ledger.\n'
                                      '\n'
                                      "The ledger lives in the operator's home directory, next to "
                                      'the other state files.\n'
                                      '"""\n'
                                      'import json\n'
                                      'import os\n'
                                      '\n'
                                      '\n'
                                      'def ledger_path():\n'
                                      '    return os.path.join(os.path.expanduser(chr(126)), '
                                      "'.omni_brain', 'notify_delivery.jsonl')\n"
                                      '\n'
                                      '\n'
                                      'def notify(title, body):\n'
                                      "    ok = os.system('logger -t estate-notify ' + title) == "
                                      '0\n'
                                      "    row = {'title': title, 'body': body, 'sent': ok}\n"
                                      "    with open(ledger_path(), 'a') as fh:\n"
                                      '        fh.write(json.dumps(row) + chr(10))\n'
                                      '    return 0 if ok else 1\n'
                                      '\n'
                                      '\n'
                                      "if __name__ == '__main__':\n"
                                      "    raise SystemExit(notify('disk full', 'root at 98 "
                                      "percent'))\n",
                     'svc/reader.py': '"""Report how many notifications were delivered today."""\n'
                                      'import json\n'
                                      '\n'
                                      "LEDGER = '/home/zixen15/.omni_brain/notify_delivery.jsonl'\n"
                                      '\n'
                                      '\n'
                                      'def count_rows(rows=None):\n'
                                      '    if rows is None:\n'
                                      "        with open(LEDGER, encoding='utf-8') as fh:\n"
                                      '            rows = [json.loads(x) for x in fh if '
                                      'x.strip()]\n'
                                      '    return len(rows)\n'},
 'notify_test': {'README.md': '# notify_test\n'
                              '\n'
                              'deliver() is called by the supervisor, which always passes a '
                              'two-word title such as\n'
                              '"disk full" or "unit failed". The tests stand in \'true\' for the '
                              'mailer so that the suite\n'
                              'does not send real alerts.\n',
                 'notify.py': '"""Deliver an alert through the configured notification '
                              'command."""\n'
                              'import os\n'
                              'import subprocess\n'
                              '\n'
                              "DEFAULT_CMD = 'estate_notify.py --send --strict'\n"
                              '\n'
                              '\n'
                              'def deliver(title, body):\n'
                              "    cmd = os.environ.get('ESTATE_NOTIFY_CMD', DEFAULT_CMD)\n"
                              "    line = cmd + ' --title ' + title + ' --body ' + body\n"
                              '    return subprocess.call(line, shell=True)\n',
                 'test_notify.py': '"""Tests for notify.deliver."""\n'
                                   'import os\n'
                                   '\n'
                                   "os.environ['ESTATE_NOTIFY_CMD'] = 'true'\n"
                                   'import notify\n'
                                   '\n'
                                   '\n'
                                   'def test_deliver_returns_zero_on_success():\n'
                                   "    assert notify.deliver('disk full', 'root at 98 percent') "
                                   '== 0\n'
                                   '\n'
                                   '\n'
                                   'def test_deliver_with_single_word_title():\n'
                                   "    assert notify.deliver('alert', 'body') == 0\n"},
 'notify_test_ren': {'README.md': '# notify_test\n'
                                  '\n'
                                  'deliver_v2() is called by the supervisor, which always passes a '
                                  'two-word title such as\n'
                                  '"disk full" or "unit failed". The tests stand in \'true\' for '
                                  'the mailer so that the suite\n'
                                  'does not send real alerts.\n',
                     'notify.py': '"""Deliver an alert through the configured notification '
                                  'command."""\n'
                                  'import os\n'
                                  'import subprocess\n'
                                  '\n'
                                  "DEFAULT_CMD_v2 = 'estate_notify.py --send --strict'\n"
                                  '\n'
                                  '\n'
                                  'def deliver_v2(title, body):\n'
                                  "    cmd = os.environ.get('ESTATE_NOTIFY_CMD', DEFAULT_CMD_v2)\n"
                                  "    line = cmd + ' --title ' + title + ' --body ' + body\n"
                                  '    return subprocess.call(line, shell=True)\n',
                     'test_notify.py': '"""Tests for notify.deliver_v2."""\n'
                                       'import os\n'
                                       '\n'
                                       "os.environ['ESTATE_NOTIFY_CMD'] = 'true'\n"
                                       'import notify\n'
                                       '\n'
                                       '\n'
                                       'def test_deliver_returns_zero_on_success_v2():\n'
                                       "    assert notify.deliver_v2('disk full', 'root at 98 "
                                       "percent') == 0\n"
                                       '\n'
                                       '\n'
                                       'def test_deliver_with_single_word_title_v2():\n'
                                       "    assert notify.deliver_v2('alert', 'body') == 0\n"},
 'notify_test_svc': {'svc/README.md': '# notify_test\n'
                                      '\n'
                                      'deliver() is called by the supervisor, which always passes '
                                      'a two-word title such as\n'
                                      '"disk full" or "unit failed". The tests stand in \'true\' '
                                      'for the mailer so that the suite\n'
                                      'does not send real alerts.\n',
                     'svc/notify.py': '"""Deliver an alert through the configured notification '
                                      'command."""\n'
                                      'import os\n'
                                      'import subprocess\n'
                                      '\n'
                                      "DEFAULT_CMD = 'estate_notify.py --send --strict'\n"
                                      '\n'
                                      '\n'
                                      'def deliver(title, body):\n'
                                      "    cmd = os.environ.get('ESTATE_NOTIFY_CMD', DEFAULT_CMD)\n"
                                      "    line = cmd + ' --title ' + title + ' --body ' + body\n"
                                      '    return subprocess.call(line, shell=True)\n',
                     'svc/test_notify.py': '"""Tests for notify.deliver."""\n'
                                           'import os\n'
                                           '\n'
                                           "os.environ['ESTATE_NOTIFY_CMD'] = 'true'\n"
                                           'import notify\n'
                                           '\n'
                                           '\n'
                                           'def test_deliver_returns_zero_on_success():\n'
                                           "    assert notify.deliver('disk full', 'root at 98 "
                                           "percent') == 0\n"
                                           '\n'
                                           '\n'
                                           'def test_deliver_with_single_word_title():\n'
                                           "    assert notify.deliver('alert', 'body') == 0\n"},
 'parametrized_parse': {'parse.py': '"""Classify a file name by the shape of its data."""\n'
                                    '\n'
                                    '\n'
                                    'def kind_of(name):\n'
                                    '    if name.endswith(".jsonl"):\n'
                                    '        return "jsonl"\n'
                                    '    if name.endswith(".json"):\n'
                                    '        return "json"\n'
                                    '    return None\n'
                                    '\n',
                        'test_parse.py': '"""Every shape, including the one that is not data at '
                                         'all."""\n'
                                         'import pytest\n'
                                         '\n'
                                         'from parse import kind_of\n'
                                         '\n'
                                         '\n'
                                         '@pytest.mark.parametrize("name,expected", [\n'
                                         '    ("a.jsonl", "jsonl"),\n'
                                         '    ("b.json", "json"),\n'
                                         '    ("c.txt", None),\n'
                                         '])\n'
                                         'def test_kind_of(name, expected):\n'
                                         '    assert kind_of(name) == expected\n'
                                         '\n'},
 'parametrized_parse_ren': {'parse.py': '"""Classify a file name by the shape of its data."""\n'
                                        '\n'
                                        '\n'
                                        'def kind_of_v2(name):\n'
                                        '    if name.endswith(".jsonl"):\n'
                                        '        return "jsonl"\n'
                                        '    if name.endswith(".json"):\n'
                                        '        return "json"\n'
                                        '    return None\n'
                                        '\n',
                            'test_parse.py': '"""Every shape, including the one that is not data '
                                             'at all."""\n'
                                             'import pytest\n'
                                             '\n'
                                             'from parse import kind_of_v2\n'
                                             '\n'
                                             '\n'
                                             '@pytest.mark.parametrize("name,expected", [\n'
                                             '    ("a.jsonl", "jsonl"),\n'
                                             '    ("b.json", "json"),\n'
                                             '    ("c.txt", None),\n'
                                             '])\n'
                                             'def test_kind_of_v2(name, expected):\n'
                                             '    assert kind_of_v2(name) == expected\n'
                                             '\n'},
 'parametrized_parse_svc': {'svc/parse.py': '"""Classify a file name by the shape of its data."""\n'
                                            '\n'
                                            '\n'
                                            'def kind_of(name):\n'
                                            '    if name.endswith(".jsonl"):\n'
                                            '        return "jsonl"\n'
                                            '    if name.endswith(".json"):\n'
                                            '        return "json"\n'
                                            '    return None\n'
                                            '\n',
                            'svc/test_parse.py': '"""Every shape, including the one that is not '
                                                 'data at all."""\n'
                                                 'import pytest\n'
                                                 '\n'
                                                 'from parse import kind_of\n'
                                                 '\n'
                                                 '\n'
                                                 '@pytest.mark.parametrize("name,expected", [\n'
                                                 '    ("a.jsonl", "jsonl"),\n'
                                                 '    ("b.json", "json"),\n'
                                                 '    ("c.txt", None),\n'
                                                 '])\n'
                                                 'def test_kind_of(name, expected):\n'
                                                 '    assert kind_of(name) == expected\n'
                                                 '\n'},
 'pipeline_pipefail': {'check_headings.sh': '#!/bin/bash\n'
                                            'set -euo pipefail\n'
                                            'ERRORS=/srv/memory/ERRORS.md\n'
                                            'echo "headings:"\n'
                                            'grep -o "^### " "$ERRORS" | tail -n 3\n'
                                            'echo "done"\n'
                                            '\n'},
 'pipeline_pipefail_ren': {'check_headings.sh': '#!/bin/bash\n'
                                                'set -euo pipefail\n'
                                                'ERRORS_v2=/srv/memory/ERRORS_v2.md\n'
                                                'echo "headings:"\n'
                                                'grep -o "^### " "$ERRORS_v2" | tail -n 3\n'
                                                'echo "done"\n'
                                                '\n'},
 'pipeline_pipefail_svc': {'svc/check_headings.sh': '#!/bin/bash\n'
                                                    'set -euo pipefail\n'
                                                    'ERRORS=/srv/memory/ERRORS.md\n'
                                                    'echo "headings:"\n'
                                                    'grep -o "^### " "$ERRORS" | tail -n 3\n'
                                                    'echo "done"\n'
                                                    '\n'},
 'printed_and_tested': {'appender.py': '"""Append the fragment, refusing a duplicate heading."""\n'
                                       'import sys\n'
                                       '\n'
                                       'ERRORS = "/srv/memory/ERRORS.md"\n'
                                       '\n'
                                       '\n'
                                       'def main(fragment):\n'
                                       '    with open(ERRORS, "a", encoding="utf-8") as fh:\n'
                                       '        fh.write(open(fragment, encoding="utf-8").read())\n'
                                       '    heads = [ln for ln in open(ERRORS, encoding="utf-8") '
                                       'if ln.startswith("### ")]\n'
                                       '    dup = len(heads) != len(set(heads))\n'
                                       '    print("duplicate headings: %s" % dup)\n'
                                       '    if dup:\n'
                                       '        print("REFUSING: the append duplicated a '
                                       'heading")\n'
                                       '        return 1\n'
                                       '    return 0\n'
                                       '\n'
                                       '\n'
                                       'if __name__ == "__main__":\n'
                                       '    sys.exit(main(sys.argv[1]))\n'
                                       '\n'},
 'printed_and_tested_ren': {'appender.py': '"""Append the fragment, refusing a duplicate '
                                           'heading."""\n'
                                           'import sys\n'
                                           '\n'
                                           'ERRORS_v2 = "/srv/memory/ERRORS_v2.md"\n'
                                           '\n'
                                           '\n'
                                           'def main(fragment):\n'
                                           '    with open(ERRORS_v2, "a", encoding="utf-8") as '
                                           'fh:\n'
                                           '        fh.write(open(fragment, '
                                           'encoding="utf-8").read())\n'
                                           '    heads = [ln for ln in open(ERRORS_v2, '
                                           'encoding="utf-8") if ln.startswith("### ")]\n'
                                           '    dup = len(heads) != len(set(heads))\n'
                                           '    print("duplicate headings: %s" % dup)\n'
                                           '    if dup:\n'
                                           '        print("REFUSING: the append duplicated a '
                                           'heading")\n'
                                           '        return 1\n'
                                           '    return 0\n'
                                           '\n'
                                           '\n'
                                           'if __name__ == "__main__":\n'
                                           '    sys.exit(main(sys.argv[1]))\n'
                                           '\n'},
 'printed_and_tested_svc': {'svc/appender.py': '"""Append the fragment, refusing a duplicate '
                                               'heading."""\n'
                                               'import sys\n'
                                               '\n'
                                               'ERRORS = "/srv/memory/ERRORS.md"\n'
                                               '\n'
                                               '\n'
                                               'def main(fragment):\n'
                                               '    with open(ERRORS, "a", encoding="utf-8") as '
                                               'fh:\n'
                                               '        fh.write(open(fragment, '
                                               'encoding="utf-8").read())\n'
                                               '    heads = [ln for ln in open(ERRORS, '
                                               'encoding="utf-8") if ln.startswith("### ")]\n'
                                               '    dup = len(heads) != len(set(heads))\n'
                                               '    print("duplicate headings: %s" % dup)\n'
                                               '    if dup:\n'
                                               '        print("REFUSING: the append duplicated a '
                                               'heading")\n'
                                               '        return 1\n'
                                               '    return 0\n'
                                               '\n'
                                               '\n'
                                               'if __name__ == "__main__":\n'
                                               '    sys.exit(main(sys.argv[1]))\n'
                                               '\n'},
 'printed_check': {'appender.py': '"""Append the fragment and report the duplicate-heading '
                                  'check."""\n'
                                  'import sys\n'
                                  '\n'
                                  'ERRORS = "/srv/memory/ERRORS.md"\n'
                                  '\n'
                                  '\n'
                                  'def main(fragment):\n'
                                  '    with open(ERRORS, "a", encoding="utf-8") as fh:\n'
                                  '        fh.write(open(fragment, encoding="utf-8").read())\n'
                                  '    heads = [ln for ln in open(ERRORS, encoding="utf-8") if '
                                  'ln.startswith("### ")]\n'
                                  '    print("duplicate headings: %s" % (len(heads) != '
                                  'len(set(heads))))\n'
                                  '    return 0\n'
                                  '\n'
                                  '\n'
                                  'if __name__ == "__main__":\n'
                                  '    sys.exit(main(sys.argv[1]))\n'
                                  '\n'},
 'printed_check_ren': {'appender.py': '"""Append the fragment and report the duplicate-heading '
                                      'check."""\n'
                                      'import sys\n'
                                      '\n'
                                      'ERRORS_v2 = "/srv/memory/ERRORS_v2.md"\n'
                                      '\n'
                                      '\n'
                                      'def main(fragment):\n'
                                      '    with open(ERRORS_v2, "a", encoding="utf-8") as fh:\n'
                                      '        fh.write(open(fragment, encoding="utf-8").read())\n'
                                      '    heads = [ln for ln in open(ERRORS_v2, encoding="utf-8") '
                                      'if ln.startswith("### ")]\n'
                                      '    print("duplicate headings: %s" % (len(heads) != '
                                      'len(set(heads))))\n'
                                      '    return 0\n'
                                      '\n'
                                      '\n'
                                      'if __name__ == "__main__":\n'
                                      '    sys.exit(main(sys.argv[1]))\n'
                                      '\n'},
 'printed_check_svc': {'svc/appender.py': '"""Append the fragment and report the duplicate-heading '
                                          'check."""\n'
                                          'import sys\n'
                                          '\n'
                                          'ERRORS = "/srv/memory/ERRORS.md"\n'
                                          '\n'
                                          '\n'
                                          'def main(fragment):\n'
                                          '    with open(ERRORS, "a", encoding="utf-8") as fh:\n'
                                          '        fh.write(open(fragment, '
                                          'encoding="utf-8").read())\n'
                                          '    heads = [ln for ln in open(ERRORS, '
                                          'encoding="utf-8") if ln.startswith("### ")]\n'
                                          '    print("duplicate headings: %s" % (len(heads) != '
                                          'len(set(heads))))\n'
                                          '    return 0\n'
                                          '\n'
                                          '\n'
                                          'if __name__ == "__main__":\n'
                                          '    sys.exit(main(sys.argv[1]))\n'
                                          '\n'},
 'quota_check': {'quota.py': '"""Decide whether a tenant is inside its storage quota."""\n'
                             '\n'
                             '\n'
                             'def is_within_quota(usage, max_limit):\n'
                             '    if usage <= max_limit:\n'
                             '        return True\n'
                             '    return False\n'
                             '\n'},
 'quota_check_svc': {'svc/quota.py': '"""Decide whether a tenant is inside its storage quota."""\n'
                                     '\n'
                                     '\n'
                                     'def is_within_quota(usage, max_limit):\n'
                                     '    if usage <= max_limit:\n'
                                     '        return True\n'
                                     '    return False\n'
                                     '\n'},
 'ready_wait': {'wait_ready.sh': '#!/bin/sh\n'
                                 '# The worker writes a ready file. Wait for it, and fail if it '
                                 'never appears.\n'
                                 'READY=/run/estate/ready\n'
                                 'i=0\n'
                                 'while [ "$i" -lt 30 ]; do\n'
                                 '    if [ -f "$READY" ]; then\n'
                                 '        echo "ready"\n'
                                 '        exit 0\n'
                                 '    fi\n'
                                 '    i=$((i + 1))\n'
                                 '    sleep 1\n'
                                 'done\n'
                                 'echo "NOT READY after 30s"\n'
                                 'exit 1\n'
                                 '\n'},
 'ready_wait_ren': {'wait_ready.sh': '#!/bin/sh\n'
                                     '# The worker writes a ready file. Wait for it, and fail if '
                                     'it never appears.\n'
                                     'READY_v2=/run/estate/ready\n'
                                     'i=0\n'
                                     'while [ "$i" -lt 30 ]; do\n'
                                     '    if [ -f "$READY_v2" ]; then\n'
                                     '        echo "ready"\n'
                                     '        exit 0\n'
                                     '    fi\n'
                                     '    i=$((i + 1))\n'
                                     '    sleep 1\n'
                                     'done\n'
                                     'echo "NOT READY_v2 after 30s"\n'
                                     'exit 1\n'
                                     '\n'},
 'ready_wait_svc': {'svc/wait_ready.sh': '#!/bin/sh\n'
                                         '# The worker writes a ready file. Wait for it, and fail '
                                         'if it never appears.\n'
                                         'READY=/run/estate/ready\n'
                                         'i=0\n'
                                         'while [ "$i" -lt 30 ]; do\n'
                                         '    if [ -f "$READY" ]; then\n'
                                         '        echo "ready"\n'
                                         '        exit 0\n'
                                         '    fi\n'
                                         '    i=$((i + 1))\n'
                                         '    sleep 1\n'
                                         'done\n'
                                         'echo "NOT READY after 30s"\n'
                                         'exit 1\n'
                                         '\n'},
 'retry_bounded': {'retry.py': '"""Retry a flaky call a bounded number of times, then give up '
                               'loudly."""\n'
                               'import time\n'
                               '\n'
                               'ATTEMPTS = 4\n'
                               '\n'
                               '\n'
                               'def attempt_then_backoff(fn, sleep=time.sleep):\n'
                               '    delay = 0.05\n'
                               '    for _ in range(ATTEMPTS):\n'
                               '        try:\n'
                               '            return fn()\n'
                               '        except OSError:\n'
                               '            sleep(delay)\n'
                               '            delay *= 2\n'
                               '    raise RuntimeError("gave up after %d attempts" % ATTEMPTS)\n'
                               '\n',
                   'test_retry.py': '"""The retry gives up after ATTEMPTS tries, and says so."""\n'
                                    'import pytest\n'
                                    '\n'
                                    'from retry import ATTEMPTS, attempt_then_backoff\n'
                                    '\n'
                                    '\n'
                                    'def test_gives_up():\n'
                                    '    calls = []\n'
                                    '\n'
                                    '    def boom():\n'
                                    '        calls.append(1)\n'
                                    '        raise OSError("down")\n'
                                    '\n'
                                    '    with pytest.raises(RuntimeError):\n'
                                    '        attempt_then_backoff(boom, sleep=lambda s: None)\n'
                                    '    assert len(calls) == ATTEMPTS\n'
                                    '\n'},
 'retry_bounded_ren': {'retry.py': '"""Retry a flaky call a bounded number of times, then give up '
                                   'loudly."""\n'
                                   'import time\n'
                                   '\n'
                                   'ATTEMPTS_v2 = 4\n'
                                   '\n'
                                   '\n'
                                   'def attempt_then_backoff_v2(fn, sleep=time.sleep):\n'
                                   '    delay = 0.05\n'
                                   '    for _ in range(ATTEMPTS_v2):\n'
                                   '        try:\n'
                                   '            return fn()\n'
                                   '        except OSError:\n'
                                   '            sleep(delay)\n'
                                   '            delay *= 2\n'
                                   '    raise RuntimeError("gave up after %d attempts" % '
                                   'ATTEMPTS_v2)\n'
                                   '\n',
                       'test_retry.py': '"""The retry gives up after ATTEMPTS_v2 tries, and says '
                                        'so."""\n'
                                        'import pytest\n'
                                        '\n'
                                        'from retry import ATTEMPTS_v2, attempt_then_backoff_v2\n'
                                        '\n'
                                        '\n'
                                        'def test_gives_up_v2():\n'
                                        '    calls = []\n'
                                        '\n'
                                        '    def boom():\n'
                                        '        calls.append(1)\n'
                                        '        raise OSError("down")\n'
                                        '\n'
                                        '    with pytest.raises(RuntimeError):\n'
                                        '        attempt_then_backoff_v2(boom, sleep=lambda s: '
                                        'None)\n'
                                        '    assert len(calls) == ATTEMPTS_v2\n'
                                        '\n'},
 'retry_bounded_svc': {'svc/retry.py': '"""Retry a flaky call a bounded number of times, then give '
                                       'up loudly."""\n'
                                       'import time\n'
                                       '\n'
                                       'ATTEMPTS = 4\n'
                                       '\n'
                                       '\n'
                                       'def attempt_then_backoff(fn, sleep=time.sleep):\n'
                                       '    delay = 0.05\n'
                                       '    for _ in range(ATTEMPTS):\n'
                                       '        try:\n'
                                       '            return fn()\n'
                                       '        except OSError:\n'
                                       '            sleep(delay)\n'
                                       '            delay *= 2\n'
                                       '    raise RuntimeError("gave up after %d attempts" % '
                                       'ATTEMPTS)\n'
                                       '\n',
                       'svc/test_retry.py': '"""The retry gives up after ATTEMPTS tries, and says '
                                            'so."""\n'
                                            'import pytest\n'
                                            '\n'
                                            'from retry import ATTEMPTS, attempt_then_backoff\n'
                                            '\n'
                                            '\n'
                                            'def test_gives_up():\n'
                                            '    calls = []\n'
                                            '\n'
                                            '    def boom():\n'
                                            '        calls.append(1)\n'
                                            '        raise OSError("down")\n'
                                            '\n'
                                            '    with pytest.raises(RuntimeError):\n'
                                            '        attempt_then_backoff(boom, sleep=lambda s: '
                                            'None)\n'
                                            '    assert len(calls) == ATTEMPTS\n'
                                            '\n'},
 'scanner_var_marker': {'backup/README': 'Archived checkouts live here. scan_marker.sh excludes '
                                         'nothing; it is the needle\n'
                                         'in its own source that must not match, which is why the '
                                         'needle is assembled.\n'
                                         '\n',
                        'scan_marker.sh': '#!/bin/sh\n'
                                          '# Fail the build when the planted marker is present. '
                                          'The needle is assembled so\n'
                                          '# this script is not itself a match when it scans its '
                                          'own directory.\n'
                                          'ROOT=$(cd "$(dirname "$0")" && pwd)\n'
                                          'MARKER=PLANTED_SECRET\n'
                                          'if grep -r "$MARKER=" "$ROOT" >/dev/null 2>&1; then\n'
                                          '    echo "marker present"\n'
                                          '    exit 1\n'
                                          'fi\n'
                                          'echo "clean"\n'
                                          'exit 0\n'
                                          '\n'},
 'scanner_var_marker_ren': {'backup/README': 'Archived checkouts live here. scan_marker.sh '
                                             'excludes nothing; it is the needle\n'
                                             'in its own source that must not match, which is why '
                                             'the needle is assembled.\n'
                                             '\n',
                            'scan_marker.sh': '#!/bin/sh\n'
                                              '# Fail the build when the planted marker is '
                                              'present. The needle is assembled so\n'
                                              '# this script is not itself a match when it scans '
                                              'its own directory.\n'
                                              'ROOT_v2=$(cd "$(dirname "$0")" && pwd)\n'
                                              'MARKER=PLANTED_SECRET\n'
                                              'if grep -r "$MARKER=" "$ROOT_v2" >/dev/null 2>&1; '
                                              'then\n'
                                              '    echo "marker present"\n'
                                              '    exit 1\n'
                                              'fi\n'
                                              'echo "clean"\n'
                                              'exit 0\n'
                                              '\n'},
 'scanner_var_marker_svc': {'svc/backup/README': 'Archived checkouts live here. scan_marker.sh '
                                                 'excludes nothing; it is the needle\n'
                                                 'in its own source that must not match, which is '
                                                 'why the needle is assembled.\n'
                                                 '\n',
                            'svc/scan_marker.sh': '#!/bin/sh\n'
                                                  '# Fail the build when the planted marker is '
                                                  'present. The needle is assembled so\n'
                                                  '# this script is not itself a match when it '
                                                  'scans its own directory.\n'
                                                  'ROOT=$(cd "$(dirname "$0")" && pwd)\n'
                                                  'MARKER=PLANTED_SECRET\n'
                                                  'if grep -r "$MARKER=" "$ROOT" >/dev/null 2>&1; '
                                                  'then\n'
                                                  '    echo "marker present"\n'
                                                  '    exit 1\n'
                                                  'fi\n'
                                                  'echo "clean"\n'
                                                  'exit 0\n'
                                                  '\n'},
 'self_grep_build': {'README.md': '# scan_repo\n'
                                  '\n'
                                  'Runs in CI before packaging. It looks for a planted credential '
                                  'marker in the checkout.\n'
                                  '\n',
                     'scan_repo.sh': '#!/bin/sh\n'
                                     '# Fail the build if a planted credential slipped into the '
                                     'checkout.\n'
                                     'ROOT=$(cd "$(dirname "$0")" && pwd)\n'
                                     'if rg -q "TODO_SECRET=" "$ROOT"; then\n'
                                     '    echo "credential present"\n'
                                     '    exit 1\n'
                                     'fi\n'
                                     'echo "clean"\n'
                                     'exit 0\n'
                                     '\n'},
 'self_grep_build_ren': {'README.md': '# scan_repo\n'
                                      '\n'
                                      'Runs in CI before packaging. It looks for a planted '
                                      'credential marker in the checkout.\n'
                                      '\n',
                         'scan_repo.sh': '#!/bin/sh\n'
                                         '# Fail the build if a planted credential slipped into '
                                         'the checkout.\n'
                                         'ROOT_v2=$(cd "$(dirname "$0")" && pwd)\n'
                                         'if rg -q "TODO_SECRET=" "$ROOT_v2"; then\n'
                                         '    echo "credential present"\n'
                                         '    exit 1\n'
                                         'fi\n'
                                         'echo "clean"\n'
                                         'exit 0\n'
                                         '\n'},
 'self_grep_build_svc': {'svc/README.md': '# scan_repo\n'
                                          '\n'
                                          'Runs in CI before packaging. It looks for a planted '
                                          'credential marker in the checkout.\n'
                                          '\n',
                         'svc/scan_repo.sh': '#!/bin/sh\n'
                                             '# Fail the build if a planted credential slipped '
                                             'into the checkout.\n'
                                             'ROOT=$(cd "$(dirname "$0")" && pwd)\n'
                                             'if rg -q "TODO_SECRET=" "$ROOT"; then\n'
                                             '    echo "credential present"\n'
                                             '    exit 1\n'
                                             'fi\n'
                                             'echo "clean"\n'
                                             'exit 0\n'
                                             '\n'},
 'signed_tag_guard': {'deploy.service': '[Unit]\n'
                                        'Description=deploy a signed tag\n'
                                        '\n'
                                        '[Service]\n'
                                        'Type=oneshot\n'
                                        'ExecStart=/opt/app/deploy_tag_guard.sh %i\n'
                                        '\n',
                      'deploy_tag_guard.sh': '#!/bin/sh\n'
                                             '# Refuse to deploy an unsigned tag, and say why with '
                                             'a distinct exit code.\n'
                                             'TAG="$1"\n'
                                             'if [ -z "$TAG" ]; then\n'
                                             '    echo "usage: deploy_tag_guard.sh TAG"\n'
                                             '    exit 2\n'
                                             'fi\n'
                                             'if ! git tag -v "$TAG" >/dev/null 2>&1; then\n'
                                             '    echo "tag not signed: $TAG"\n'
                                             '    exit 3\n'
                                             'fi\n'
                                             'echo "signed: $TAG"\n'
                                             'exit 0\n'
                                             '\n'},
 'signed_tag_guard_ren': {'deploy.service': '[Unit]\n'
                                            'Description=deploy a signed tag\n'
                                            '\n'
                                            '[Service]\n'
                                            'Type=oneshot\n'
                                            'ExecStart=/opt/app/deploy_tag_guard.sh %i\n'
                                            '\n',
                          'deploy_tag_guard.sh': '#!/bin/sh\n'
                                                 '# Refuse to deploy an unsigned tag, and say why '
                                                 'with a distinct exit code.\n'
                                                 'TAG_v2="$1"\n'
                                                 'if [ -z "$TAG_v2" ]; then\n'
                                                 '    echo "usage: deploy_tag_guard.sh TAG_v2"\n'
                                                 '    exit 2\n'
                                                 'fi\n'
                                                 'if ! git tag -v "$TAG_v2" >/dev/null 2>&1; then\n'
                                                 '    echo "tag not signed: $TAG_v2"\n'
                                                 '    exit 3\n'
                                                 'fi\n'
                                                 'echo "signed: $TAG_v2"\n'
                                                 'exit 0\n'
                                                 '\n'},
 'signed_tag_guard_svc': {'svc/deploy.service': '[Unit]\n'
                                                'Description=deploy a signed tag\n'
                                                '\n'
                                                '[Service]\n'
                                                'Type=oneshot\n'
                                                'ExecStart=/opt/app/deploy_tag_guard.sh %i\n'
                                                '\n',
                          'svc/deploy_tag_guard.sh': '#!/bin/sh\n'
                                                     '# Refuse to deploy an unsigned tag, and say '
                                                     'why with a distinct exit code.\n'
                                                     'TAG="$1"\n'
                                                     'if [ -z "$TAG" ]; then\n'
                                                     '    echo "usage: deploy_tag_guard.sh TAG"\n'
                                                     '    exit 2\n'
                                                     'fi\n'
                                                     'if ! git tag -v "$TAG" >/dev/null 2>&1; '
                                                     'then\n'
                                                     '    echo "tag not signed: $TAG"\n'
                                                     '    exit 3\n'
                                                     'fi\n'
                                                     'echo "signed: $TAG"\n'
                                                     'exit 0\n'
                                                     '\n'},
 'space_report': {'crontab.txt': '*/15 * * * * /usr/bin/python3 /opt/app/diskcheck.py\n\n',
                  'diskcheck.py': '"""Check that the data volume has room, and tell cron whether '
                                  'it does."""\n'
                                  'import shutil\n'
                                  'import sys\n'
                                  '\n'
                                  'FLOOR_GB = 5\n'
                                  '\n'
                                  '\n'
                                  'def free_gb(path="/srv/data"):\n'
                                  '    return shutil.disk_usage(path).free // (1024 ** 3)\n'
                                  '\n'
                                  '\n'
                                  'def main():\n'
                                  '    free = free_gb()\n'
                                  '    if free < FLOOR_GB:\n'
                                  '        print("LOW SPACE: %dGB" % free)\n'
                                  '    else:\n'
                                  '        print("space fine: %dGB" % free)\n'
                                  '    return 0\n'
                                  '\n'
                                  '\n'
                                  'if __name__ == "__main__":\n'
                                  '    sys.exit(main())\n'
                                  '\n'},
 'space_report_ren': {'crontab.txt': '*/15 * * * * /usr/bin/python3 /opt/app/diskcheck.py\n\n',
                      'diskcheck.py': '"""Check that the data volume has room, and tell cron '
                                      'whether it does."""\n'
                                      'import shutil\n'
                                      'import sys\n'
                                      '\n'
                                      'FLOOR_GB_v2 = 5\n'
                                      '\n'
                                      '\n'
                                      'def free_gb_v2(path="/srv/data"):\n'
                                      '    return shutil.disk_usage(path).free // (1024 ** 3)\n'
                                      '\n'
                                      '\n'
                                      'def main():\n'
                                      '    free = free_gb_v2()\n'
                                      '    if free < FLOOR_GB_v2:\n'
                                      '        print("LOW SPACE: %dGB" % free)\n'
                                      '    else:\n'
                                      '        print("space fine: %dGB" % free)\n'
                                      '    return 0\n'
                                      '\n'
                                      '\n'
                                      'if __name__ == "__main__":\n'
                                      '    sys.exit(main())\n'
                                      '\n'},
 'space_report_svc': {'svc/crontab.txt': '*/15 * * * * /usr/bin/python3 /opt/app/diskcheck.py\n\n',
                      'svc/diskcheck.py': '"""Check that the data volume has room, and tell cron '
                                          'whether it does."""\n'
                                          'import shutil\n'
                                          'import sys\n'
                                          '\n'
                                          'FLOOR_GB = 5\n'
                                          '\n'
                                          '\n'
                                          'def free_gb(path="/srv/data"):\n'
                                          '    return shutil.disk_usage(path).free // (1024 ** 3)\n'
                                          '\n'
                                          '\n'
                                          'def main():\n'
                                          '    free = free_gb()\n'
                                          '    if free < FLOOR_GB:\n'
                                          '        print("LOW SPACE: %dGB" % free)\n'
                                          '    else:\n'
                                          '        print("space fine: %dGB" % free)\n'
                                          '    return 0\n'
                                          '\n'
                                          '\n'
                                          'if __name__ == "__main__":\n'
                                          '    sys.exit(main())\n'
                                          '\n'},
 'state_remember': {'agent.py': '"""Handle each task once, using the state file as the record of '
                                'what was done."""\n'
                                'from state import load, remember\n'
                                '\n'
                                '\n'
                                'def run(tasks, handler):\n'
                                '    """Handle each task once: dedupe ACROSS runs and WITHIN this '
                                'batch."""\n'
                                '    seen = load()\n'
                                '    handled = []\n'
                                '    for key in tasks:\n'
                                '        if seen.get(key):\n'
                                '            continue\n'
                                '        handler(key)\n'
                                '        remember(key)\n'
                                '        seen[key] = True\n'
                                '        handled.append(key)\n'
                                '    return handled\n'
                                '\n',
                    'state.py': '"""Track which keys the agent has already handled; one writer, '
                                'atomic replace."""\n'
                                'import json\n'
                                'import os\n'
                                'from pathlib import Path\n'
                                '\n'
                                'SEEN = Path.home() / ".local" / "state" / "agent" / "seen.json"\n'
                                '\n'
                                '\n'
                                'def load():\n'
                                '    if not SEEN.exists():\n'
                                '        return {}\n'
                                '    return json.loads(SEEN.read_text(encoding="utf-8"))\n'
                                '\n'
                                '\n'
                                'def remember(key):\n'
                                '    """Record the key and say whether it was NEW; that '
                                'distinction is the point."""\n'
                                '    data = load()\n'
                                '    new = key not in data\n'
                                '    data[key] = True\n'
                                '    SEEN.parent.mkdir(parents=True, exist_ok=True)\n'
                                '    tmp = SEEN.with_suffix(".writing")\n'
                                '    with open(tmp, "w", encoding="utf-8") as fh:\n'
                                '        fh.write(json.dumps(data))\n'
                                '        fh.flush()\n'
                                '        os.fsync(fh.fileno())\n'
                                '    os.replace(tmp, SEEN)\n'
                                '    return new\n'
                                '\n'},
 'state_remember_ren': {'agent.py': '"""Handle each task once, using the state file as the record '
                                    'of what was done."""\n'
                                    'from state import load_v2, remember_v2\n'
                                    '\n'
                                    '\n'
                                    'def run_v2(tasks, handler):\n'
                                    '    """Handle each task once: dedupe ACROSS runs and WITHIN '
                                    'this batch."""\n'
                                    '    seen = load_v2()\n'
                                    '    handled = []\n'
                                    '    for key in tasks:\n'
                                    '        if seen.get(key):\n'
                                    '            continue\n'
                                    '        handler(key)\n'
                                    '        remember_v2(key)\n'
                                    '        seen[key] = True\n'
                                    '        handled.append(key)\n'
                                    '    return handled\n'
                                    '\n',
                        'state.py': '"""Track which keys the agent has already handled; one '
                                    'writer, atomic replace."""\n'
                                    'import json\n'
                                    'import os\n'
                                    'from pathlib import Path\n'
                                    '\n'
                                    'SEEN = Path.home() / ".local" / "state" / "agent" / '
                                    '"seen.json"\n'
                                    '\n'
                                    '\n'
                                    'def load_v2():\n'
                                    '    if not SEEN.exists():\n'
                                    '        return {}\n'
                                    '    return json.loads(SEEN.read_text(encoding="utf-8"))\n'
                                    '\n'
                                    '\n'
                                    'def remember_v2(key):\n'
                                    '    """Record the key and say whether it was NEW; that '
                                    'distinction is the point."""\n'
                                    '    data = load_v2()\n'
                                    '    new = key not in data\n'
                                    '    data[key] = True\n'
                                    '    SEEN.parent.mkdir(parents=True, exist_ok=True)\n'
                                    '    tmp = SEEN.with_suffix(".writing")\n'
                                    '    with open(tmp, "w", encoding="utf-8") as fh:\n'
                                    '        fh.write(json.dumps(data))\n'
                                    '        fh.flush()\n'
                                    '        os.fsync(fh.fileno())\n'
                                    '    os.replace(tmp, SEEN)\n'
                                    '    return new\n'
                                    '\n'},
 'state_remember_svc': {'svc/agent.py': '"""Handle each task once, using the state file as the '
                                        'record of what was done."""\n'
                                        'from state import load, remember\n'
                                        '\n'
                                        '\n'
                                        'def run(tasks, handler):\n'
                                        '    """Handle each task once: dedupe ACROSS runs and '
                                        'WITHIN this batch."""\n'
                                        '    seen = load()\n'
                                        '    handled = []\n'
                                        '    for key in tasks:\n'
                                        '        if seen.get(key):\n'
                                        '            continue\n'
                                        '        handler(key)\n'
                                        '        remember(key)\n'
                                        '        seen[key] = True\n'
                                        '        handled.append(key)\n'
                                        '    return handled\n'
                                        '\n',
                        'svc/state.py': '"""Track which keys the agent has already handled; one '
                                        'writer, atomic replace."""\n'
                                        'import json\n'
                                        'import os\n'
                                        'from pathlib import Path\n'
                                        '\n'
                                        'SEEN = Path.home() / ".local" / "state" / "agent" / '
                                        '"seen.json"\n'
                                        '\n'
                                        '\n'
                                        'def load():\n'
                                        '    if not SEEN.exists():\n'
                                        '        return {}\n'
                                        '    return json.loads(SEEN.read_text(encoding="utf-8"))\n'
                                        '\n'
                                        '\n'
                                        'def remember(key):\n'
                                        '    """Record the key and say whether it was NEW; that '
                                        'distinction is the point."""\n'
                                        '    data = load()\n'
                                        '    new = key not in data\n'
                                        '    data[key] = True\n'
                                        '    SEEN.parent.mkdir(parents=True, exist_ok=True)\n'
                                        '    tmp = SEEN.with_suffix(".writing")\n'
                                        '    with open(tmp, "w", encoding="utf-8") as fh:\n'
                                        '        fh.write(json.dumps(data))\n'
                                        '        fh.flush()\n'
                                        '        os.fsync(fh.fileno())\n'
                                        '    os.replace(tmp, SEEN)\n'
                                        '    return new\n'
                                        '\n'},
 'units_guard': {'check_units_strict.sh': '#!/bin/sh\n'
                                          '# Failure must reach the caller: exit 3 on down, 0 only '
                                          'when active.\n'
                                          'if systemctl is-active --quiet '
                                          'estate-heartbeat.service; then\n'
                                          '    echo "heartbeat active"\n'
                                          '    exit 0\n'
                                          'fi\n'
                                          'echo "HEARTBEAT DOWN"\n'
                                          'exit 3\n'
                                          '\n',
                 'fetch.py': '"""Read a timeout from the environment."""\n'
                             'import os\n'
                             '\n'
                             '\n'
                             'def timeout():\n'
                             '    return int(os.environ.get("HTTP_TIMEOUT", "5"))\n'
                             '\n',
                 'scan_excluding_self.sh': '#!/bin/sh\n'
                                           '# The scanner must not match its own source, so it '
                                           'excludes itself by name.\n'
                                           'ROOT=$(cd "$(dirname "$0")" && pwd)\n'
                                           'SELF=$(basename "$0")\n'
                                           'if grep -r --exclude="$SELF" "PLANTED_SECRET=" '
                                           '"$ROOT"; then\n'
                                           '    echo "credential present"\n'
                                           '    exit 1\n'
                                           'fi\n'
                                           'echo "clean"\n'
                                           'exit 0\n'
                                           '\n',
                 'test_config.py': '"""The test configures a real value; nothing is replaced."""\n'
                                   'import os\n'
                                   '\n'
                                   'import fetch\n'
                                   '\n'
                                   '\n'
                                   'def test_timeout_is_used(monkeypatch):\n'
                                   '    monkeypatch.setenv("HTTP_TIMEOUT", "1")\n'
                                   '    assert fetch.timeout() == 1\n'
                                   '\n'},
 'units_guard_ren': {'check_units_strict.sh': '#!/bin/sh\n'
                                              '# Failure must reach the caller: exit 3 on down, 0 '
                                              'only when active.\n'
                                              'if systemctl is-active --quiet '
                                              'estate-heartbeat.service; then\n'
                                              '    echo "heartbeat active"\n'
                                              '    exit 0\n'
                                              'fi\n'
                                              'echo "HEARTBEAT DOWN"\n'
                                              'exit 3\n'
                                              '\n',
                     'fetch.py': '"""Read a timeout_v2 from the environment."""\n'
                                 'import os\n'
                                 '\n'
                                 '\n'
                                 'def timeout_v2():\n'
                                 '    return int(os.environ.get("HTTP_TIMEOUT", "5"))\n'
                                 '\n',
                     'scan_excluding_self.sh': '#!/bin/sh\n'
                                               '# The scanner must not match its own source, so it '
                                               'excludes itself by name.\n'
                                               'ROOT_v2=$(cd "$(dirname "$0")" && pwd)\n'
                                               'SELF_v2=$(basename "$0")\n'
                                               'if grep -r --exclude="$SELF_v2" "PLANTED_SECRET=" '
                                               '"$ROOT_v2"; then\n'
                                               '    echo "credential present"\n'
                                               '    exit 1\n'
                                               'fi\n'
                                               'echo "clean"\n'
                                               'exit 0\n'
                                               '\n',
                     'test_config.py': '"""The test configures a real value; nothing is '
                                       'replaced."""\n'
                                       'import os\n'
                                       '\n'
                                       'import fetch\n'
                                       '\n'
                                       '\n'
                                       'def test_timeout_is_used_v2(monkeypatch):\n'
                                       '    monkeypatch.setenv("HTTP_TIMEOUT", "1")\n'
                                       '    assert fetch.timeout_v2() == 1\n'
                                       '\n'},
 'units_guard_svc': {'svc/check_units_strict.sh': '#!/bin/sh\n'
                                                  '# Failure must reach the caller: exit 3 on '
                                                  'down, 0 only when active.\n'
                                                  'if systemctl is-active --quiet '
                                                  'estate-heartbeat.service; then\n'
                                                  '    echo "heartbeat active"\n'
                                                  '    exit 0\n'
                                                  'fi\n'
                                                  'echo "HEARTBEAT DOWN"\n'
                                                  'exit 3\n'
                                                  '\n',
                     'svc/fetch.py': '"""Read a timeout from the environment."""\n'
                                     'import os\n'
                                     '\n'
                                     '\n'
                                     'def timeout():\n'
                                     '    return int(os.environ.get("HTTP_TIMEOUT", "5"))\n'
                                     '\n',
                     'svc/scan_excluding_self.sh': '#!/bin/sh\n'
                                                   '# The scanner must not match its own source, '
                                                   'so it excludes itself by name.\n'
                                                   'ROOT=$(cd "$(dirname "$0")" && pwd)\n'
                                                   'SELF=$(basename "$0")\n'
                                                   'if grep -r --exclude="$SELF" "PLANTED_SECRET=" '
                                                   '"$ROOT"; then\n'
                                                   '    echo "credential present"\n'
                                                   '    exit 1\n'
                                                   'fi\n'
                                                   'echo "clean"\n'
                                                   'exit 0\n'
                                                   '\n',
                     'svc/test_config.py': '"""The test configures a real value; nothing is '
                                           'replaced."""\n'
                                           'import os\n'
                                           '\n'
                                           'import fetch\n'
                                           '\n'
                                           '\n'
                                           'def test_timeout_is_used(monkeypatch):\n'
                                           '    monkeypatch.setenv("HTTP_TIMEOUT", "1")\n'
                                           '    assert fetch.timeout() == 1\n'
                                           '\n'}}

TRUTH = {'append_verified': {'also': [],
                     'class': None,
                     'expect': 'clean',
                     'file': 'appender.py',
                     'line': 20,
                     'needle': 'if p.returncode != 0'},
 'append_verified_ren': {'also': [],
                         'class': None,
                         'expect': 'clean',
                         'file': 'appender.py',
                         'line': 20,
                         'needle': 'if p.returncode != 0'},
 'append_verified_svc': {'also': [],
                         'class': None,
                         'expect': 'clean',
                         'file': 'svc/appender.py',
                         'line': 20,
                         'needle': 'if p.returncode != 0'},
 'audit_ignored': {'also': ['report.py'],
                   'class': 'record-unread',
                   'expect': 'defect',
                   'file': 'store.py',
                   'line': 5,
                   'needle': 'Path.home()'},
 'audit_ignored_ren': {'also': ['report.py'],
                       'class': 'record-unread',
                       'expect': 'defect',
                       'file': 'store.py',
                       'line': 5,
                       'needle': 'Path.home()'},
 'audit_ignored_svc': {'also': ['svc/report.py'],
                       'class': 'record-unread',
                       'expect': 'defect',
                       'file': 'svc/store.py',
                       'line': 5,
                       'needle': 'Path.home()'},
 'check_units': {'also': [],
                 'class': 'check-cannot-fail',
                 'expect': 'defect',
                 'file': 'check_units.sh',
                 'line': 6,
                 'needle': 'HEARTBEAT DOWN'},
 'check_units_svc': {'also': [],
                     'class': 'check-cannot-fail',
                     'expect': 'defect',
                     'file': 'svc/check_units.sh',
                     'line': 6,
                     'needle': 'HEARTBEAT DOWN'},
 'checksum_guard': {'also': [],
                    'class': None,
                    'expect': 'clean',
                    'file': 'main.py',
                    'line': 10,
                    'needle': 'return 2'},
 'checksum_guard_ren': {'also': [],
                        'class': None,
                        'expect': 'clean',
                        'file': 'main.py',
                        'line': 10,
                        'needle': 'return 2'},
 'checksum_guard_svc': {'also': [],
                        'class': None,
                        'expect': 'clean',
                        'file': 'svc/main.py',
                        'line': 10,
                        'needle': 'return 2'},
 'disk_guard': {'also': [],
                'class': 'check-cannot-fail',
                'expect': 'defect',
                'file': 'check_disk.py',
                'line': 12,
                'needle': 'DISK-OVER-LIMIT'},
 'disk_guard_ren': {'also': [],
                    'class': 'check-cannot-fail',
                    'expect': 'defect',
                    'file': 'check_disk.py',
                    'line': 12,
                    'needle': 'DISK-OVER-LIMIT'},
 'disk_guard_svc': {'also': [],
                    'class': 'check-cannot-fail',
                    'expect': 'defect',
                    'file': 'svc/check_disk.py',
                    'line': 12,
                    'needle': 'DISK-OVER-LIMIT'},
 'env_default_agrees': {'also': [],
                        'class': None,
                        'expect': 'clean',
                        'file': 'settings.py',
                        'line': 2,
                        'needle': 'DEFAULT_ENDPOINT'},
 'env_default_agrees_ren': {'also': [],
                            'class': None,
                            'expect': 'clean',
                            'file': 'settings.py',
                            'line': 2,
                            'needle': 'DEFAULT_ENDPOINT'},
 'env_default_agrees_svc': {'also': [],
                            'class': None,
                            'expect': 'clean',
                            'file': 'svc/settings.py',
                            'line': 2,
                            'needle': 'DEFAULT_ENDPOINT'},
 'fragment_pair': {'also': [],
                   'class': 'record-unread',
                   'expect': 'defect',
                   'file': 'appender.py',
                   'line': 4,
                   'needle': 'FE, FH ='},
 'fragment_pair_ren': {'also': [],
                       'class': 'record-unread',
                       'expect': 'defect',
                       'file': 'appender.py',
                       'line': 4,
                       'needle': 'FE, FH ='},
 'fragment_pair_svc': {'also': [],
                       'class': 'record-unread',
                       'expect': 'defect',
                       'file': 'svc/appender.py',
                       'line': 4,
                       'needle': 'FE, FH ='},
 'fragment_pair_used': {'also': [],
                        'class': None,
                        'expect': 'clean',
                        'file': 'appender.py',
                        'line': 16,
                        'needle': 'append(FH, HISTORY)'},
 'fragment_pair_used_ren': {'also': [],
                            'class': None,
                            'expect': 'clean',
                            'file': 'appender.py',
                            'line': 16,
                            'needle': 'append(FH, HISTORY)'},
 'fragment_pair_used_svc': {'also': [],
                            'class': None,
                            'expect': 'clean',
                            'file': 'svc/appender.py',
                            'line': 16,
                            'needle': 'append(FH, HISTORY)'},
 'guard_after_normalise': {'also': [],
                           'class': None,
                           'expect': 'clean',
                           'file': 'appender.py',
                           'line': 12,
                           'needle': 'if not body.endswith'},
 'guard_after_normalise_ren': {'also': [],
                               'class': None,
                               'expect': 'clean',
                               'file': 'appender.py',
                               'line': 12,
                               'needle': 'if not body.endswith'},
 'guard_after_normalise_svc': {'also': [],
                               'class': None,
                               'expect': 'clean',
                               'file': 'svc/appender.py',
                               'line': 12,
                               'needle': 'if not body.endswith'},
 'home_paths_agree': {'also': [],
                      'class': None,
                      'expect': 'clean',
                      'file': 'paths.py',
                      'line': 4,
                      'needle': 'LEDGER'},
 'home_paths_agree_ren': {'also': [],
                          'class': None,
                          'expect': 'clean',
                          'file': 'paths.py',
                          'line': 4,
                          'needle': 'LEDGER'},
 'home_paths_agree_svc': {'also': [],
                          'class': None,
                          'expect': 'clean',
                          'file': 'svc/paths.py',
                          'line': 4,
                          'needle': 'LEDGER'},
 'label_parser': {'also': [],
                  'class': None,
                  'expect': 'clean',
                  'file': 'labels.py',
                  'line': 5,
                  'needle': 'label_of'},
 'label_parser_ren': {'also': [],
                      'class': None,
                      'expect': 'clean',
                      'file': 'labels.py',
                      'line': 5,
                      'needle': 'label_of'},
 'label_parser_svc': {'also': [],
                      'class': None,
                      'expect': 'clean',
                      'file': 'svc/labels.py',
                      'line': 5,
                      'needle': 'label_of'},
 'layout_shared_root': {'also': [],
                        'class': None,
                        'expect': 'clean',
                        'file': 'layout.py',
                        'line': 7,
                        'needle': 'def under'},
 'layout_shared_root_ren': {'also': [],
                            'class': None,
                            'expect': 'clean',
                            'file': 'layout.py',
                            'line': 7,
                            'needle': 'def under'},
 'layout_shared_root_svc': {'also': [],
                            'class': None,
                            'expect': 'clean',
                            'file': 'svc/layout.py',
                            'line': 7,
                            'needle': 'def under'},
 'leak_sentinel': {'also': [],
                   'class': 'control-reads-own-text',
                   'expect': 'defect',
                   'file': 'sentinel.sh',
                   'line': 4,
                   'needle': 'grep -r "PLANTED_SECRET="'},
 'leak_sentinel_ren': {'also': [],
                       'class': 'control-reads-own-text',
                       'expect': 'defect',
                       'file': 'sentinel.sh',
                       'line': 4,
                       'needle': 'grep -r "PLANTED_SECRET="'},
 'leak_sentinel_svc': {'also': [],
                       'class': 'control-reads-own-text',
                       'expect': 'defect',
                       'file': 'svc/sentinel.sh',
                       'line': 4,
                       'needle': 'grep -r "PLANTED_SECRET="'},
 'ledger_split': {'also': ['dashboard.py'],
                  'class': 'record-unread',
                  'expect': 'defect',
                  'file': 'audit.py',
                  'line': 7,
                  'needle': 'Path.home()'},
 'ledger_split_ren': {'also': ['dashboard.py'],
                      'class': 'record-unread',
                      'expect': 'defect',
                      'file': 'audit.py',
                      'line': 7,
                      'needle': 'Path.home()'},
 'ledger_split_svc': {'also': ['svc/dashboard.py'],
                      'class': 'record-unread',
                      'expect': 'defect',
                      'file': 'svc/audit.py',
                      'line': 7,
                      'needle': 'Path.home()'},
 'masked_pipeline': {'also': [],
                     'class': 'check-cannot-fail',
                     'expect': 'defect',
                     'file': 'check_headings.sh',
                     'line': 5,
                     'needle': 'grep -o "^### " "$ERRORS" | tail -n 3'},
 'masked_pipeline_svc': {'also': [],
                         'class': 'check-cannot-fail',
                         'expect': 'defect',
                         'file': 'svc/check_headings.sh',
                         'line': 5,
                         'needle': 'grep -o "^### " "$ERRORS" | tail -n 3'},
 'mem_guard': {'also': [],
               'class': None,
               'expect': 'clean',
               'file': 'check_mem.py',
               'line': 12,
               'needle': 'MEM-OVER-LIMIT'},
 'mem_guard_ren': {'also': [],
                   'class': None,
                   'expect': 'clean',
                   'file': 'check_mem.py',
                   'line': 12,
                   'needle': 'MEM-OVER-LIMIT'},
 'mem_guard_svc': {'also': [],
                   'class': None,
                   'expect': 'clean',
                   'file': 'svc/check_mem.py',
                   'line': 12,
                   'needle': 'MEM-OVER-LIMIT'},
 'memory_append': {'also': [],
                   'class': 'check-cannot-fail',
                   'expect': 'defect',
                   'file': 'appender.py',
                   'line': 17,
                   'needle': 'subprocess.run(args)'},
 'memory_append_ren': {'also': [],
                       'class': 'check-cannot-fail',
                       'expect': 'defect',
                       'file': 'appender.py',
                       'line': 17,
                       'needle': 'subprocess.run(args)'},
 'memory_append_svc': {'also': [],
                       'class': 'check-cannot-fail',
                       'expect': 'defect',
                       'file': 'svc/appender.py',
                       'line': 17,
                       'needle': 'subprocess.run(args)'},
 'mock_external': {'also': [],
                   'class': None,
                   'expect': 'clean',
                   'file': 'test_fetch.py',
                   'line': 8,
                   'needle': 'urllib.request.urlopen'},
 'mock_external_ren': {'also': [],
                       'class': None,
                       'expect': 'clean',
                       'file': 'test_fetch.py',
                       'line': 8,
                       'needle': 'urllib.request.urlopen'},
 'mock_external_svc': {'also': [],
                       'class': None,
                       'expect': 'clean',
                       'file': 'svc/test_fetch.py',
                       'line': 8,
                       'needle': 'urllib.request.urlopen'},
 'mock_self_assert': {'also': [],
                      'class': 'test-replaces-subject',
                      'expect': 'defect',
                      'file': 'test_sender.py',
                      'line': 9,
                      'needle': 'sender.deliver = mock.Mock'},
 'mock_self_assert_ren': {'also': [],
                          'class': 'test-replaces-subject',
                          'expect': 'defect',
                          'file': 'test_sender.py',
                          'line': 9,
                          'needle': 'sender.deliver = mock.Mock'},
 'mock_self_assert_svc': {'also': [],
                          'class': 'test-replaces-subject',
                          'expect': 'defect',
                          'file': 'svc/test_sender.py',
                          'line': 9,
                          'needle': 'sender.deliver = mock.Mock'},
 'mock_subject': {'also': [],
                  'class': 'test-replaces-subject',
                  'expect': 'defect',
                  'file': 'test_report.py',
                  'line': 4,
                  'needle': 'REPORT_CMD'},
 'mock_subject_ren': {'also': [],
                      'class': 'test-replaces-subject',
                      'expect': 'defect',
                      'file': 'test_report.py',
                      'line': 4,
                      'needle': 'REPORT_CMD'},
 'mock_subject_svc': {'also': [],
                      'class': 'test-replaces-subject',
                      'expect': 'defect',
                      'file': 'svc/test_report.py',
                      'line': 4,
                      'needle': 'REPORT_CMD'},
 'normalise_then_test': {'also': [],
                         'class': 'check-cannot-fail',
                         'expect': 'defect',
                         'file': 'appender.py',
                         'line': 12,
                         'needle': 'if chr(13) in body'},
 'normalise_then_test_ren': {'also': [],
                             'class': 'check-cannot-fail',
                             'expect': 'defect',
                             'file': 'appender.py',
                             'line': 12,
                             'needle': 'if chr(13) in body'},
 'normalise_then_test_svc': {'also': [],
                             'class': 'check-cannot-fail',
                             'expect': 'defect',
                             'file': 'svc/appender.py',
                             'line': 12,
                             'needle': 'if chr(13) in body'},
 'notify_path': {'also': [],
                 'class': 'record-unread',
                 'expect': 'defect',
                 'file': 'notify.py',
                 'line': 10,
                 'needle': 'expanduser(chr(126))'},
 'notify_path_ren': {'also': [],
                     'class': 'record-unread',
                     'expect': 'defect',
                     'file': 'notify.py',
                     'line': 10,
                     'needle': 'expanduser(chr(126))'},
 'notify_path_svc': {'also': [],
                     'class': 'record-unread',
                     'expect': 'defect',
                     'file': 'svc/notify.py',
                     'line': 10,
                     'needle': 'expanduser(chr(126))'},
 'notify_test': {'also': [],
                 'class': 'test-replaces-subject',
                 'expect': 'defect',
                 'file': 'test_notify.py',
                 'line': 4,
                 'needle': "ESTATE_NOTIFY_CMD'] = 'true'"},
 'notify_test_ren': {'also': [],
                     'class': 'test-replaces-subject',
                     'expect': 'defect',
                     'file': 'test_notify.py',
                     'line': 4,
                     'needle': "ESTATE_NOTIFY_CMD'] = 'true'"},
 'notify_test_svc': {'also': [],
                     'class': 'test-replaces-subject',
                     'expect': 'defect',
                     'file': 'svc/test_notify.py',
                     'line': 4,
                     'needle': "ESTATE_NOTIFY_CMD'] = 'true'"},
 'parametrized_parse': {'also': [],
                        'class': None,
                        'expect': 'clean',
                        'file': 'test_parse.py',
                        'line': 7,
                        'needle': 'parametrize'},
 'parametrized_parse_ren': {'also': [],
                            'class': None,
                            'expect': 'clean',
                            'file': 'test_parse.py',
                            'line': 7,
                            'needle': 'parametrize'},
 'parametrized_parse_svc': {'also': [],
                            'class': None,
                            'expect': 'clean',
                            'file': 'svc/test_parse.py',
                            'line': 7,
                            'needle': 'parametrize'},
 'pipeline_pipefail': {'also': [],
                       'class': None,
                       'expect': 'clean',
                       'file': 'check_headings.sh',
                       'line': 2,
                       'needle': 'set -euo pipefail'},
 'pipeline_pipefail_ren': {'also': [],
                           'class': None,
                           'expect': 'clean',
                           'file': 'check_headings.sh',
                           'line': 2,
                           'needle': 'set -euo pipefail'},
 'pipeline_pipefail_svc': {'also': [],
                           'class': None,
                           'expect': 'clean',
                           'file': 'svc/check_headings.sh',
                           'line': 2,
                           'needle': 'set -euo pipefail'},
 'printed_and_tested': {'also': [],
                        'class': None,
                        'expect': 'clean',
                        'file': 'appender.py',
                        'line': 13,
                        'needle': 'if dup:'},
 'printed_and_tested_ren': {'also': [],
                            'class': None,
                            'expect': 'clean',
                            'file': 'appender.py',
                            'line': 13,
                            'needle': 'if dup:'},
 'printed_and_tested_svc': {'also': [],
                            'class': None,
                            'expect': 'clean',
                            'file': 'svc/appender.py',
                            'line': 13,
                            'needle': 'if dup:'},
 'printed_check': {'also': [],
                   'class': 'check-cannot-fail',
                   'expect': 'defect',
                   'file': 'appender.py',
                   'line': 11,
                   'needle': 'print("duplicate headings'},
 'printed_check_ren': {'also': [],
                       'class': 'check-cannot-fail',
                       'expect': 'defect',
                       'file': 'appender.py',
                       'line': 11,
                       'needle': 'print("duplicate headings'},
 'printed_check_svc': {'also': [],
                       'class': 'check-cannot-fail',
                       'expect': 'defect',
                       'file': 'svc/appender.py',
                       'line': 11,
                       'needle': 'print("duplicate headings'},
 'quota_check': {'also': [],
                 'class': None,
                 'expect': 'clean',
                 'file': 'quota.py',
                 'line': 4,
                 'needle': 'is_within_quota'},
 'quota_check_svc': {'also': [],
                     'class': None,
                     'expect': 'clean',
                     'file': 'svc/quota.py',
                     'line': 4,
                     'needle': 'is_within_quota'},
 'ready_wait': {'also': [],
                'class': None,
                'expect': 'clean',
                'file': 'wait_ready.sh',
                'line': 14,
                'needle': 'exit 1'},
 'ready_wait_ren': {'also': [],
                    'class': None,
                    'expect': 'clean',
                    'file': 'wait_ready.sh',
                    'line': 14,
                    'needle': 'exit 1'},
 'ready_wait_svc': {'also': [],
                    'class': None,
                    'expect': 'clean',
                    'file': 'svc/wait_ready.sh',
                    'line': 14,
                    'needle': 'exit 1'},
 'retry_bounded': {'also': [],
                   'class': None,
                   'expect': 'clean',
                   'file': 'retry.py',
                   'line': 15,
                   'needle': 'raise RuntimeError'},
 'retry_bounded_ren': {'also': [],
                       'class': None,
                       'expect': 'clean',
                       'file': 'retry.py',
                       'line': 15,
                       'needle': 'raise RuntimeError'},
 'retry_bounded_svc': {'also': [],
                       'class': None,
                       'expect': 'clean',
                       'file': 'svc/retry.py',
                       'line': 15,
                       'needle': 'raise RuntimeError'},
 'scanner_var_marker': {'also': [],
                        'class': None,
                        'expect': 'clean',
                        'file': 'scan_marker.sh',
                        'line': 5,
                        'needle': 'MARKER='},
 'scanner_var_marker_ren': {'also': [],
                            'class': None,
                            'expect': 'clean',
                            'file': 'scan_marker.sh',
                            'line': 5,
                            'needle': 'MARKER='},
 'scanner_var_marker_svc': {'also': [],
                            'class': None,
                            'expect': 'clean',
                            'file': 'svc/scan_marker.sh',
                            'line': 5,
                            'needle': 'MARKER='},
 'self_grep_build': {'also': [],
                     'class': 'control-reads-own-text',
                     'expect': 'defect',
                     'file': 'scan_repo.sh',
                     'line': 4,
                     'needle': 'rg -q'},
 'self_grep_build_ren': {'also': [],
                         'class': 'control-reads-own-text',
                         'expect': 'defect',
                         'file': 'scan_repo.sh',
                         'line': 4,
                         'needle': 'rg -q'},
 'self_grep_build_svc': {'also': [],
                         'class': 'control-reads-own-text',
                         'expect': 'defect',
                         'file': 'svc/scan_repo.sh',
                         'line': 4,
                         'needle': 'rg -q'},
 'signed_tag_guard': {'also': [],
                      'class': None,
                      'expect': 'clean',
                      'file': 'deploy_tag_guard.sh',
                      'line': 10,
                      'needle': 'exit 3'},
 'signed_tag_guard_ren': {'also': [],
                          'class': None,
                          'expect': 'clean',
                          'file': 'deploy_tag_guard.sh',
                          'line': 10,
                          'needle': 'exit 3'},
 'signed_tag_guard_svc': {'also': [],
                          'class': None,
                          'expect': 'clean',
                          'file': 'svc/deploy_tag_guard.sh',
                          'line': 10,
                          'needle': 'exit 3'},
 'space_report': {'also': [],
                  'class': 'check-cannot-fail',
                  'expect': 'defect',
                  'file': 'diskcheck.py',
                  'line': 15,
                  'needle': 'LOW SPACE'},
 'space_report_ren': {'also': [],
                      'class': 'check-cannot-fail',
                      'expect': 'defect',
                      'file': 'diskcheck.py',
                      'line': 15,
                      'needle': 'LOW SPACE'},
 'space_report_svc': {'also': [],
                      'class': 'check-cannot-fail',
                      'expect': 'defect',
                      'file': 'svc/diskcheck.py',
                      'line': 15,
                      'needle': 'LOW SPACE'},
 'state_remember': {'also': [],
                    'class': None,
                    'expect': 'clean',
                    'file': 'state.py',
                    'line': 6,
                    'needle': 'SEEN'},
 'state_remember_ren': {'also': [],
                        'class': None,
                        'expect': 'clean',
                        'file': 'state.py',
                        'line': 6,
                        'needle': 'SEEN'},
 'state_remember_svc': {'also': [],
                        'class': None,
                        'expect': 'clean',
                        'file': 'svc/state.py',
                        'line': 6,
                        'needle': 'SEEN'},
 'units_guard': {'also': [],
                 'class': None,
                 'expect': 'clean',
                 'file': 'check_units_strict.sh',
                 'line': 2,
                 'needle': 'exit 3'},
 'units_guard_ren': {'also': [],
                     'class': None,
                     'expect': 'clean',
                     'file': 'check_units_strict.sh',
                     'line': 2,
                     'needle': 'exit 3'},
 'units_guard_svc': {'also': [],
                     'class': None,
                     'expect': 'clean',
                     'file': 'svc/check_units_strict.sh',
                     'line': 2,
                     'needle': 'exit 3'}}
