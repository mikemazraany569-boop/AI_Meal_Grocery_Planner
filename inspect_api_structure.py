
from pathlib import Path

ROOT = Path(__file__).resolve().parent

DIRECTORIES = [
    "src",
    "src/api",
    "src/rag",
    "frontend",
]

IMPORTANT_FILES = [
    "main.py",
    "app.py",
    "api.py",
    "server.py",
    "requirements.txt",
    "pyproject.toml",
]

print("=" * 70)
print("API STRUCTURE INSPECTION — READ ONLY")
print("=" * 70)

for directory in DIRECTORIES:
    path = ROOT / directory
    print(f"\n[{directory}]")

    if not path.exists():
        print("  Directory does not exist.")
        continue

    for item in sorted(path.rglob("*")):
        if not item.is_file():
            continue

        if any(part in {".venv", "__pycache__", ".git"}
               for part in item.parts):
            continue

        print(f"  {item.relative_to(ROOT)}")

print("\n" + "=" * 70)
print("IMPORTANT FILE CONTENTS")
print("=" * 70)

for directory in ["src", "frontend"]:
    base = ROOT / directory

    if not base.exists():
        continue

    for path in sorted(base.rglob("*.py")):
        if any(part in {".venv", "__pycache__", ".git"}
               for part in path.parts):
            continue

        print(f"\n\n{'=' * 70}")
        print(f"FILE: {path.relative_to(ROOT)}")
        print("=" * 70)

        try:
            content = path.read_text(encoding="utf-8")

            # Limit output for large files.
            print(content[:12000])

            if len(content) > 12000:
                print("\n[FILE OUTPUT TRUNCATED]")

        except Exception as error:
            print(f"Could not read file: {error}")

print("\n" + "=" * 70)
print("INSPECTION COMPLETED — NO FILES MODIFIED")
print("=" * 70)
