
from pathlib import Path

BASE = Path(__file__).resolve().parent

TARGETS = [
    "src/rag",
    "frontend",
    "data/vector_store",
    "data/recipes",
    "data/ingredients",
]

MAX_DEPTH = 5


def show_tree(folder, prefix="", depth=0):
    if depth > MAX_DEPTH:
        return

    try:
        items = sorted(
            folder.iterdir(),
            key=lambda p: (p.is_file(), p.name.lower())
        )
    except PermissionError:
        print(prefix + "[Permission denied]")
        return

    for index, item in enumerate(items):
        last = index == len(items) - 1
        connector = "└── " if last else "├── "

        if item.is_dir():
            print(prefix + connector + item.name + "/")
            extension = "    " if last else "│   "
            show_tree(item, prefix + extension, depth + 1)
        else:
            size = item.stat().st_size
            print(prefix + connector + f"{item.name} ({size:,} bytes)")


print("=" * 60)
print("AI MEAL & GROCERY PLANNER — PROJECT STRUCTURE")
print("=" * 60)

for relative_path in TARGETS:
    folder = BASE / relative_path

    print(f"\n{relative_path}/")
    print("-" * 60)

    if folder.exists():
        show_tree(folder)
    else:
        print("[Folder does not exist]")
