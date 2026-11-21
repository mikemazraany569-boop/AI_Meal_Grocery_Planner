
import ast
from pathlib import Path

BASE = Path(__file__).resolve().parent

RAG_FILES = [
    BASE / "src/rag/recipe_document_builder.py",
    BASE / "src/rag/recipe_index_manager.py",
    BASE / "src/rag/recipe_retriever.py",
]

APP_FILE = BASE / "frontend/app.py"

KEYWORDS = (
    "rag", "retriev", "embed", "faiss", "index",
    "ollama", "api", "model", "recipe", "prompt",
    "generate", "chat", "streamlit"
)


def inspect_python_file(path):
    print("\n" + "=" * 70)
    print(path.relative_to(BASE))
    print("=" * 70)

    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    print("\nIMPORTS:")
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            print(source.splitlines()[node.lineno - 1])

    print("\nCLASSES AND METHODS:")
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            print(f"\nclass {node.name}:")
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    print(f"  {child.name} (line {child.lineno})")

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            print(f"{node.name} (line {node.lineno})")


def inspect_streamlit(path):
    print("\n" + "=" * 70)
    print("FRONTEND — RELEVANT STREAMLIT INTEGRATION")
    print("=" * 70)

    lines = path.read_text(encoding="utf-8").splitlines()

    for number, line in enumerate(lines, start=1):
        if any(word in line.lower() for word in KEYWORDS):
            print(f"{number:4}: {line.strip()}")


def main():
    for path in RAG_FILES:
        if path.exists():
            inspect_python_file(path)
        else:
            print(f"Missing: {path}")

    if APP_FILE.exists():
        inspect_streamlit(APP_FILE)
    else:
        print("Missing frontend/app.py")


if __name__ == "__main__":
    main()
