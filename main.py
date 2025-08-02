# cli/main.py
import argparse
from pathlib import Path
from core.pipeline import process_repository

def parse_args():
    parser = argparse.ArgumentParser(description="Populate missing docstrings in Python source files.")
    parser.add_argument("repo_path", type=Path, help="Path to the root of the Python repository")
    parser.add_argument("--llm", choices=["ollama", "openai"], default="ollama", help="LLM backend to use")
    parser.add_argument("--dry-run", action="store_true", help="Don't overwrite files, just show what would change")
    parser.add_argument("--backup", action="store_true", help="Create a backup of each modified file")
    parser.add_argument("--ignore", nargs="*", default=[], help="List of file or directory paths to ignore (relative to repo_path)")
    return parser.parse_args()

def main():
    args = parse_args()
    process_repository(
        root_path=args.repo_path,
        llm_backend=args.llm,
        dry_run=args.dry_run,
        create_backup=args.backup,
        ignore_list=args.ignore
    )

if __name__ == "__main__":
    main()
