from abc import ABC, abstractmethod
import requests
from models import TextCompletionRequest, TextCompletionResponse, JsonToGrammarResponse

BOS_TOKEN = "{{[INPUT]}}"
EOS_TOKEN = "{{[OUTPUT]}}"
SYSTEM_BOS_TOKEN = "{{[SYSTEM]}}"

class KoboldInterface(ABC):
    @abstractmethod
    def extract_facts(self, messages: list[dict]) -> list[dict]:
        """Extract facts from user messages"""

    @abstractmethod
    def _text_completion_gbnf(self) -> TextCompletionResponse:
        """Text completion generation w/ GBNF."""

    @abstractmethod
    def _json_to_grammar(self, schema: dict) -> str:
        "Convert json to gbnf"

    @abstractmethod
    def _apply_chat_template_to_prompt(self, prompt: str) -> str:
        """Applies BOS/EOS tokens to prompt"""

    @abstractmethod
    def _apply_chat_template_to_system(self, memory: str) -> str:
        """Applies BOS/EOS tokens to system prompt (referred as memory in koboldcpp apis)"""


class KoboldClient(KoboldInterface):
    def __init__(self, url="http://127.0.0.1:5001"):
        self.url = url

    def extract_facts(self, messages: list[dict]) -> list[dict]:
        pass

    def _text_completion_gbnf(self, memory: str, prompt: str, schema: dict) -> TextCompletionResponse:
        req = TextCompletionRequest(
            memory=self._apply_chat_template_to_system(memory),
            prompt=self._apply_chat_template_to_prompt(prompt),
            grammar=self._json_to_grammar(schema)
        )

        text_completion_resp = requests.post(
            self.url + "/api/v1/generate",
            json=req.model_dump()
        )

        return TextCompletionResponse.model_validate_json(text_completion_resp.text)

    def _json_to_grammar(self, schema: dict) -> str:
        "Convert json to gbnf"
        resp = requests.post(
            self.url + "/api/extra/json_to_grammar",
            json=schema
        )

        json_to_grammar_resp = JsonToGrammarResponse.model_validate_json(resp.text)
        return json_to_grammar_resp.result

    def _apply_chat_template_to_prompt(self, prompt: str) -> str:
        return BOS_TOKEN + prompt + EOS_TOKEN

    def _apply_chat_template_to_system(self, memory: str) -> str:
        return SYSTEM_BOS_TOKEN + memory

