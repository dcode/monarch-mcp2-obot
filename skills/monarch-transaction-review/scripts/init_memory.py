#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


DEFAULT_MEMORY_PATH = Path("~/.config/monarch/transaction-review-memory.md").expanduser()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create the private Monarch transaction review memory file."
    )
    parser.add_argument(
        "--path",
        default=str(DEFAULT_MEMORY_PATH),
        help="Memory file path. Defaults to ~/.config/monarch/transaction-review-memory.md.",
    )
    args = parser.parse_args()

    memory_path = Path(args.path).expanduser()
    if memory_path.exists():
        print(f"Memory already exists: {memory_path}")
        return

    template_path = Path(__file__).resolve().parents[1] / "references" / "memory-template.md"
    memory_path.parent.mkdir(parents=True, exist_ok=True)
    memory_path.write_text(template_path.read_text(encoding="utf-8"), encoding="utf-8")
    memory_path.chmod(0o600)
    print(f"Created memory: {memory_path}")


if __name__ == "__main__":
    main()
