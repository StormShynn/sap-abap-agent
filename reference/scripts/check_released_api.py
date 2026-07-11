#!/usr/bin/env python3
"""Check ABAP code không dùng object/keyword không released trong SAP Public Cloud 2602.

Rule danh sách xem docs/sap-knowledge/released-objects-2602.md.

Usage:
  python check_released_api.py <src-dir> [--json]
"""
import json
import re
import sys
from pathlib import Path

# (pattern, severity, message)
FORBIDDEN = [
    (r'\bCL_GUI_[A-Z_]+\b',          'ERROR', 'CL_GUI_* not released in cloud (use released equivalents)'),
    (r'\bCALL\s+TRANSACTION\b',      'ERROR', 'CALL TRANSACTION not released in cloud (use OData)'),
    (r'\bCALL\s+DIALOG\b',           'ERROR', 'CALL DIALOG not released in cloud'),
    (r'\bAUTHORITY-CHECK\b',         'ERROR', 'AUTHORITY-CHECK not released in cloud (use ABAP CDS DCL)'),
    (r'\bSET\s+USER-COMMAND\b',      'WARN',  'SET USER-COMMAND deprecated in cloud'),
    (r'\bSELECT\s+\*\s+FROM\b',      'WARN',  'SELECT * is anti-pattern (list fields explicitly)'),
    (r'\bSELECT\s+.*\s+ENDSELECT\b', 'WARN',  'SELECT ... ENDSELECT is performance issue'),
]

ABAP_FILE_EXT = re.compile(r'\.(abap|asbdef|asddls|asmd|tabl|srvd|srvb)$')


def check_dir(src: Path) -> list:
    issues = []
    for path in src.rglob('*'):
        if not path.is_file() or not ABAP_FILE_EXT.search(path.name):
            continue
        try:
            text = path.read_text(encoding='utf-8', errors='replace')
        except Exception as e:
            issues.append({
                'file': str(path.relative_to(src)),
                'severity': 'WARN',
                'message': f'Could not read file: {e}',
            })
            continue
        for i, line in enumerate(text.splitlines(), 1):
            # Skip comment lines starting with * or "
            stripped = line.lstrip()
            if stripped.startswith('*') or stripped.startswith('"') or stripped.startswith('//'):
                continue
            for pattern, severity, message in FORBIDDEN:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append({
                        'file': str(path.relative_to(src)),
                        'line': i,
                        'severity': severity,
                        'pattern': pattern,
                        'message': message,
                        'snippet': line.strip()[:100],
                    })
    return issues


def main():
    if len(sys.argv) < 2:
        print('Usage: check_released_api.py <src-dir> [--json]', file=sys.stderr)
        sys.exit(2)
    src = Path(sys.argv[1])
    json_out = '--json' in sys.argv

    issues = check_dir(src)
    if json_out:
        print(json.dumps({'issues': issues, 'count': len(issues)}, indent=2))
    else:
        errors = [i for i in issues if i['severity'] == 'ERROR']
        warns = [i for i in issues if i['severity'] == 'WARN']
        if not issues:
            print(f'✅ Released API check passed: 0 issues.')
            return 0
        print(f'Released API check: {len(errors)} error(s), {len(warns)} warning(s)')
        print()
        for issue in issues:
            icon = '❌' if issue['severity'] == 'ERROR' else '⚠'
            loc = f"{issue['file']}:{issue.get('line', '?')}"
            print(f'  {icon} {loc}: {issue["message"]}')
            if issue.get('snippet'):
                print(f'       {issue["snippet"]}')
        return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main() or 0)
