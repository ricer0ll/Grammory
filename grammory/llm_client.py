from abc import ABC, abstractmethod
from .dataclasses import Message
from .models import TextCompletionResponse

class LLMClient(ABC):
    @abstractmethod
    def extract_facts(self, messages: list[Message]) -> list[str]:
        """Extract facts from user messages, returning a list of strings (facts)"""

    @abstractmethod
    def _text_completion_gbnf(self) -> TextCompletionResponse:
        """Text completion generation w/ GBNF."""

    @abstractmethod
    def _extractable_user_facts_ispresent(self, message: Message) -> bool:
        """Checks a message, whether or not it contains some info about a user"""

    @abstractmethod
    def _json_to_grammar(self, schema: dict) -> str:
        "Convert json schema to gbnf"

    @abstractmethod
    def _apply_chat_template_to_prompt(self, prompt: str) -> str:
        """Applies BOS/EOS tokens to prompt"""

    @abstractmethod
    def _apply_chat_template_to_system(self, memory: str) -> str:
        """Applies BOS/EOS tokens to system prompt (referred as memory in koboldcpp apis)"""

