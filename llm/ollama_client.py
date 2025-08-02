# llm/ollama_client.py
import json
import ollama
from pathlib import Path
from llm.base_llm import BaseLLMClient

DEFAULT_CONFIG_PATH = Path(__file__).parent / "ollama_config.json"

def load_config(config_path: Path = DEFAULT_CONFIG_PATH) -> dict:
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[OllamaClient] Failed to load config: {e}. Using defaults.")
        return {
            "ollama_server": "http://localhost:11434",
            "model": "codellama:7b",
            "temperature": 0.7,
            "max_tokens": 1024,
            "top_p": 0.9
        }

class OllamaClient(BaseLLMClient):
    def __init__(self, config_path: Path = DEFAULT_CONFIG_PATH):
        self.config = load_config(config_path)
        self.model = self.config.get("model")
        self.server = self.config.get("ollama_server")
        ollama.base_url = self.server

    def generate_docstring(self, code_snippet: str, item_type: str, name: str) -> str:
        prompt = self._build_prompt(code_snippet, item_type, name)
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={
                    "temperature": self.config.get("temperature", 0.7),
                    "top_p": self.config.get("top_p", 0.9),
                    "num_predict": self.config.get("max_tokens", 1024)
                },
            )
            return response.get("message", {}).get("content", "")
        except Exception as e:
            print(f"[OllamaClient] Error generating docstring: {e}")
            return ""

    def _build_prompt(self, code: str, item_type: str, name: str) -> str:
        return (
            f"You are a senior Python developer. "
            f"Generate a concise and descriptive docstring for the following {item_type} named '{name}'. "
            f"Use standard Python docstring conventions.\n\n"
            f"{code}"
        )
