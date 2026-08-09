import re
import sys
from pathlib import Path

# Simple heuristic scanner for likely secrets in the repo
PATTERNS = {
    'AWS Access Key ID': re.compile(r'AKIA[0-9A-Z]{16}'),
    'Generic API Key': re.compile(r"(?i)(?:api[_-]?key|secret|token)\s*=\s*['\"]?([A-Za-z0-9-_]{16,})['\"]?"),
    'JWT-like': re.compile(r'eyJ[0-9A-Za-z_-]{10,}\.[0-9A-Za-z_-]{10,}\.[0-9A-Za-z_-]{10,}'),
    'Private-like key header': re.compile(r'-----BEGIN (?:RSA|PRIVATE) KEY-----'),
}

EXCLUDE_DIRS = {'.git', 'node_modules', '.venv', '__pycache__'}


def scan(path: Path):
    results = []
    for p in path.rglob('*'):
        if any(part in EXCLUDE_DIRS for part in p.parts):
            continue
        if p.is_file() and p.stat().st_size < 1024 * 1024:  # skip huge files
            try:
                text = p.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                continue
            for name, pat in PATTERNS.items():
                for m in pat.finditer(text):
                    snippet = m.group(0)
                    results.append((str(p), name, snippet[:200]))
    return results


if __name__ == '__main__':
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.').resolve()
    print(f"Scanning {root} for likely secrets...\n")
    findings = scan(root)
    if not findings:
        print('No likely secrets found by heuristics.')
        sys.exit(0)
    for f in findings:
        print(f"File: {f[0]} -- Pattern: {f[1]} -- Match: {f[2]}")
    print(f"\nFound {len(findings)} potential matches. Review manually.")
    sys.exit(1)
