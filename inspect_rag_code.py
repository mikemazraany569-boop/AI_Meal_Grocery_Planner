
import ast
from pathlib import Path

BASE = Path(__file__).resolve().parent

FILES = [
    BASE / "src/rag/recipe_document_builder.py",
    BASE / "src/rag/recipe_index_manager.py",
    BASE / "src/rag/recipe_retriever.py",
]

def inspect_file(path):
    print("\n" + "=" * 75)
    print(path.relative_to(BASE))
    print("=" * 75)

    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    # Imports and module-level constants
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.Assign)):
            print(ast.get_source_segment(source, node))

    # All class methods
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            print(f"\nCLASS: {node.name}")
            for method in node.body:
                if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    print("\n" + "-" * 65)
                    print(f"METHOD: {method.name}")
                    print(ast.get_source_segment(source, method))

for file in FILES:
    if file.exists():
        inspect_file(file)
    else:
        print(f"MISSING: {file}")
