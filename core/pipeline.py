# core/pipeline.py
import os
from pathlib import Path
from typing import List
import shutil
import libcst as cst
from libcst import parse_module
from libcst import CSTTransformer, FunctionDef, ClassDef, SimpleStatementLine, Expr, SimpleString
from llm.ollama_client import OllamaClient

def extract_definitions(source_code: str):
    """
    Parses the source code and extracts all function and class definitions without docstrings.
    Returns a list of (name, type, node) tuples.
    """
    class DocstringExtractor(cst.CSTVisitor):
        def __init__(self):
            self.missing_doc_items = []

        def visit_FunctionDef(self, node: FunctionDef):
            if not node.get_docstring():
                self.missing_doc_items.append((node.name.value, "function", node))

        def visit_ClassDef(self, node: ClassDef):
            if not node.get_docstring():
                self.missing_doc_items.append((node.name.value, "class", node))

    tree = cst.parse_module(source_code)
    visitor = DocstringExtractor()
    tree.visit(visitor)
    return visitor.missing_doc_items

def insert_docstrings(source_code: str, docstring_data: List[tuple]) -> str:
    """
    Inserts generated docstrings into the source code using LibCST.

    Parameters:
        source_code: The original source code.
        docstring_data: A list of tuples (name, item_type, generated_docstring).

    Returns:
        Modified source code string with inserted docstrings.
    """
    class DocstringInserter(CSTTransformer):
        def __init__(self, docstring_data):
            self.doc_map = { (name, typ): doc for name, typ, doc in docstring_data }

        def sanitize_docstring(self, doc: str) -> str:
            """
            Removes triple quotes and markdown-style code fences from the docstring.
            """
            doc = doc.strip()

            # Remove ```python fences
            if doc.startswith("```python"):
                doc = doc[len("```python"):].strip()
            if doc.endswith("```"):
                doc = doc[:-3].strip()

            # Remove "def ...:" line if it appears
            lines = doc.splitlines()
            if lines and lines[0].strip().startswith("def "):
                lines = lines[1:]
            doc = "\n".join(lines).strip()

            # Remove surrounding triple quotes if present
            if doc.startswith('"""') and doc.endswith('"""'):
                doc = doc[3:-3].strip()
            elif doc.startswith("'''") and doc.endswith("'''"):
                doc = doc[3:-3].strip()

            return doc

        
        def leave_FunctionDef(self, original_node, updated_node):
            key = (original_node.name.value, "function")
            if key in self.doc_map and not original_node.get_docstring():
                doc = self.doc_map[key]
                doc = self.sanitize_docstring(doc)
                doc_node = SimpleStatementLine(body=[Expr(value=SimpleString(f'"""{doc}"""'))])
                return updated_node.with_changes(
    body=updated_node.body.with_changes(body=[doc_node] + list(updated_node.body.body))
)

            return updated_node

        def leave_ClassDef(self, original_node, updated_node):
            key = (original_node.name.value, "class")
            if key in self.doc_map and not original_node.get_docstring():
                doc = self.doc_map[key]
                doc_node = SimpleStatementLine(body=[Expr(value=SimpleString(f'"""{doc}"""'))])
                return updated_node.with_changes(body=updated_node.body.with_changes(body=[doc_node] + updated_node.body.body))
            return updated_node

    tree = cst.parse_module(source_code)
    transformer = DocstringInserter(docstring_data)
    modified_tree = tree.visit(transformer)
    return modified_tree.code

def process_repository(root_path: Path, llm_backend: str, dry_run: bool, create_backup: bool, ignore_list: List[str]):
    """
    Recursively processes all Python files in the given repository directory.
    """
    ignore_paths = { (root_path / Path(p)).resolve() for p in ignore_list }

    if llm_backend == "ollama":
        llm = OllamaClient()
    else:
        raise NotImplementedError(f"LLM backend '{llm_backend}' is not supported yet.")

    for py_file in root_path.rglob("*.py"):
        if any(ignored in py_file.parents or py_file == ignored for ignored in ignore_paths):
            continue

        print(f"Processing: {py_file.relative_to(root_path)}")

        with open(py_file, 'r', encoding='utf-8') as f:
            source = f.read()

        missing_docs = extract_definitions(source)
        docstring_data = []

        for name, item_type, node in missing_docs:
            snippet = cst.Module([node]).code
            docstring = llm.generate_docstring(snippet, item_type, name)
            print(f"  Suggested docstring for {item_type} '{name}':")
            print(docstring)
            print("-")
            docstring_data.append((name, item_type, docstring))

        modified_source = insert_docstrings(source, docstring_data)

        if not dry_run:
            if create_backup:
                backup_path = py_file.with_suffix(py_file.suffix + ".bak")
                shutil.copy(py_file, backup_path)
            with open(py_file, 'w', encoding='utf-8') as f:
                f.write(modified_source)
