"""
sync_public.py

Scans an Obsidian vault for notes with "public: true" in frontmatter.
Copies matching notes and their referenced attachments to a Quartz
content folder, preserving directory structure.

Place this script in the root of your Quartz repo. It defaults to
writing into ./content/ relative to the script location.

Usage:
    python sync_public.py --vault /path/to/vault              # normal run
    python sync_public.py --vault /path/to/vault --dry-run    # preview only
"""

import argparse
import re
import shutil
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_VAULT = None  # must be passed via --vault
DEFAULT_QUARTZ_CONTENT = SCRIPT_DIR / "content"


def is_public(filepath: Path) -> bool:
    """Check if a note has public: true in its frontmatter."""
    try:
        lines = filepath.read_text(encoding="utf-8").splitlines()
    except (UnicodeDecodeError, OSError):
        return False

    if not lines or lines[0].strip() != "---":
        return False

    for line in lines[1:40]:
        if line.strip() == "---":
            break
        if re.match(r"^public:\s*\"?true\"?\s*$", line):
            return True

    return False


def find_attachments(filepath: Path, vault: Path) -> list[Path]:
    """Parse ![[...]] and ![](...) references and resolve them in the vault."""
    text = filepath.read_text(encoding="utf-8")
    refs = set()

    # Obsidian embeds: ![[filename.png]] or ![[folder/filename.png]]
    for match in re.finditer(r"!\[\[([^\]|]+?)(?:\|[^\]]*?)?\]\]", text):
        refs.add(match.group(1).strip())

    # Markdown images: ![alt](path)
    for match in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", text):
        ref = match.group(1).strip()
        if not ref.startswith("http"):
            refs.add(ref)

    attachments = []
    for ref in refs:
        # Try exact relative path from vault root
        candidate = vault / ref
        if candidate.is_file():
            attachments.append(candidate)
            continue

        # Obsidian shortest-path: search the whole vault for the filename
        name = Path(ref).name
        matches = list(vault.rglob(name))
        if matches:
            attachments.append(matches[0])

    return attachments


def sync(vault: Path, quartz_content: Path, dry_run: bool = False):
    notes = list(vault.rglob("*.md"))
    copied_notes = 0
    copied_attachments = 0
    attachment_set: set[Path] = set()

    # First pass: find public notes and collect their attachments
    public_notes: list[Path] = []
    for note in notes:
        if is_public(note):
            public_notes.append(note)
            for att in find_attachments(note, vault):
                attachment_set.add(att)

    if not public_notes:
        print("No public notes found.")
        return

    # Copy notes
    for note in public_notes:
        rel = note.relative_to(vault)
        dest = quartz_content / rel
        if dry_run:
            print(f"  NOTE: {rel}")
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(note, dest)
            print(f"  NOTE: {rel}")
        copied_notes += 1

    # Copy attachments
    for att in sorted(attachment_set):
        rel = att.relative_to(vault)
        dest = quartz_content / rel
        if dry_run:
            print(f"  ATT:  {rel}")
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(att, dest)
            print(f"  ATT:  {rel}")
        copied_attachments += 1

    prefix = "[DRY RUN] " if dry_run else ""
    print(f"\n{prefix}Done. {copied_notes} notes, {copied_attachments} attachments.")


def main():
    parser = argparse.ArgumentParser(description="Sync public Obsidian notes to Quartz")
    parser.add_argument("--vault", type=Path, required=True, help="Path to Obsidian vault")
    parser.add_argument("--quartz", type=Path, default=DEFAULT_QUARTZ_CONTENT, help="Path to Quartz content/ folder")
    parser.add_argument("--dry-run", action="store_true", help="Preview only, don't copy")
    args = parser.parse_args()

    if not args.vault.is_dir():
        print(f"Vault not found: {args.vault}")
        return
    if not args.quartz.is_dir() and not args.dry_run:
        args.quartz.mkdir(parents=True, exist_ok=True)

    print(f"Vault:   {args.vault}")
    print(f"Quartz:  {args.quartz}")
    print(f"Dry run: {args.dry_run}\n")

    sync(args.vault, args.quartz, args.dry_run)


if __name__ == "__main__":
    main()