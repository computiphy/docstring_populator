# llm/base_llm.py
from abc import ABC, abstractmethod

class BaseLLMClient(ABC):
    @abstractmethod
    def generate_docstring(self, code_snippet: str, item_type: str, name: str) -> str:
        """
        Generate a docstring for the given code snippet.

        Parameters:
        - code_snippet: str - The source code of the class or function.
        - item_type: str - Either 'function' or 'class'.
        - name: str - The name of the item.

        Returns:
        - A string containing the generated docstring.
        """
        pass
