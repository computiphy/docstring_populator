# Docstring Auto-Populator with LLMs

This project provides an automated solution for populating missing docstrings in Python source files using Language Learning Models (LLMs), with a modular and extensible architecture. The implementation leverages the `libcst` library to parse and modify Python code while maintaining formatting integrity.

---

## 📁 Project Structure

```
.
├── core/
│   └── pipeline.py               # Main logic for scanning, generating, and inserting docstrings
├── llm/
│   └── ollama_client.py         # Interface to interact with the Ollama LLM backend
├── main.py                      # CLI entry point for triggering the pipeline
├── README.md                    # Project documentation
```

---

## 🚀 Features

* Detects all Python `class` and `function` definitions missing docstrings.
* Uses LLMs (e.g., [Ollama](https://ollama.ai)) to auto-generate high-quality docstrings.
* Inserts the generated docstrings directly above each class/function definition.
* Optionally creates backups before modifying files.
* Skips files/folders defined in a customizable ignore list.

---

## 🛠️ How It Works

### 1. **Extraction of Missing Docstrings**

* The function `extract_definitions(source_code: str)` uses `libcst` to walk the AST of the Python file.
* It collects all function and class definitions that lack docstrings.

### 2. **Docstring Generation**

* `OllamaClient.generate_docstring()` sends the source snippet (a function/class) to an LLM like Ollama.
* Returns a docstring, typically wrapped with Markdown/code block formatting.

### 3. **Sanitization**

* `DocstringInserter.sanitize_docstring()` removes:

  * Triple quotes (`"""`, `'''`)
  * Markdown code fences (`python ... `)
  * Function signatures accidentally included by the model

### 4. **Docstring Insertion**

* `insert_docstrings()` uses `libcst`'s `CSTTransformer` to programmatically add docstrings to AST nodes.
* Ensures formatting and indentation remain intact.

### 5. **Repository Traversal**

* `process_repository()` recursively walks through `.py` files in a given path.
* It integrates the above steps to process all eligible files, handling backup and dry-run modes.

---

## 🔧 Usage

### 1. **Install Requirements**

```bash
pip install -r requirements.txt
```

### 2. **Run the Pipeline**

```bash
python main.py --repo /path/to/repo --llm ollama --dry-run
```

### 3. **Options**

| Flag        | Description                                 |
| ----------- | ------------------------------------------- |
| `--repo`    | Path to your Python project folder          |
| `--llm`     | Backend to use for docstring generation     |
| `--dry-run` | Shows output without modifying files        |
| `--backup`  | Creates `.bak` backup before changing files |
| `--ignore`  | Comma-separated paths to exclude            |

---

## 🔌 LLM Integration (Ollama)

`llm/ollama_client.py` handles communication with the Ollama server. It expects a local Ollama instance to be running.

You can replace this backend by implementing a new client under `llm/` with the same interface.

---

## 🧪 Example

Given this input:

```python
def add(x, y):
    return x + y
```

Will be transformed into:

```python
def add(x, y):
    """
    Adds two numbers and returns the result.

    Parameters:
    - x: First number
    - y: Second number

    Returns:
    - Sum of x and y
    """
    return x + y
```

---

## 🧱 Dependencies

* `libcst`
* `pathlib`
* `shutil`
* `ollama` (or any other LLM backend)

---

## 👨‍💻 Contributing

Feel free to fork and open PRs for enhancements, bugfixes, or new features.

