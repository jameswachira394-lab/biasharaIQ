"""
Redact common secrets from working-tree files.

This script replaces values for known env keys in-place with placeholders
and creates a git commit with the changes. It does NOT rewrite Git history.

Run locally and verify before pushing. Backup repo before running history-rewrite tools.
"""
import re
from pathlib import Path
import subprocess
import sys

REPLACEMENTS = {
    # env file keys -> replacement
    r"^(SECRET_KEY\s*=\s*).+$": r"\1REDACTED_IN_REPO",
    r"^(GEMINI_API_KEY\s*=\s*).+$": r"\1REDACTED_IN_REPO",
    r"^(JWT_SECRET\s*=\s*).+$": r"\1REDACTED_IN_REPO",
    r"^(POSTGRES_PASSWORD\s*=\s*).+$": r"\1REDACTED_IN_REPO",
    r"^(DB_PASSWORD\s*=\s*).+$": r"\1REDACTED_IN_REPO",
    r"(AKIA[0-9A-Z]{16})": r"REDACTED_AWS_KEY",
}

TARGET_FILES = [
    ".env",
    "frontend/.env.production",
]


def redact_file(path: Path) -> bool:
    try:
        text = path.read_text(encoding='utf-8')
    except FileNotFoundError:
        return False

    original = text
    for pat, repl in REPLACEMENTS.items():
        text = re.sub(pat, repl, text, flags=re.MULTILINE)

    if text != original:
        path.write_text(text, encoding='utf-8')
        return True
    return False


def git_commit(msg: str):
    subprocess.check_call(['git', 'add', '.'])
    subprocess.check_call(['git', 'commit', '-m', msg])


def main():
    repo_root = Path('.').resolve()
    changed = []
    for f in TARGET_FILES:
        p = repo_root / f
        if redact_file(p):
            changed.append(str(p))

    # also redact terraform state files (in-place)
    for tf in repo_root.glob('terraform/*.tfstate*'):
        if redact_file(tf):
            changed.append(str(tf))

    if not changed:
        print("No files changed.")
        return 0

    print("Redacted values in:")
    for c in changed:
        print(" -", c)

    try:
        git_commit('chore: redact secrets from working tree (placeholders)')
        print("Committed redaction. Consider rotating any leaked secrets and rewriting history with git-filter-repo or BFG.")
    except Exception as e:
        print("Failed to commit changes automatically:", e)
        print("Please review changes and commit manually.")

    return 0


if __name__ == '__main__':
    sys.exit(main())
