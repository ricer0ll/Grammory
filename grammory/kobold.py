from abc import ABC, abstractmethod
import requests
import json
from .models import TextCompletionRequest, TextCompletionResponse, JsonToGrammarResponse
from .dataclasses import Message, Memory
from .prompts import EXTRACT_FACT_SYSTEM_PROMPT, CHECK_FOR_EXTRACTABLE_USER_FACTS_PROMPT
from .grammar import EXTRACT_FACTS_JSON_SCHEMA, EXTRACTABLE_FACTS_CHECK_GRAMMER

BOS_TOKEN = "{{[INPUT]}}"
EOS_TOKEN = "{{[OUTPUT]}}"
SYSTEM_BOS_TOKEN = "{{[SYSTEM]}}"

class KoboldInterface(ABC):
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


class KoboldClient(KoboldInterface):
    def __init__(self, url="http://127.0.0.1:5001"):
        self.url = url

    def extract_facts(self, messages: list[Message]) -> list[str]:
        grammar = self._json_to_grammar(EXTRACT_FACTS_JSON_SCHEMA)
        memory = EXTRACT_FACT_SYSTEM_PROMPT
        extractable_facts_messages: list[Message] = []

        for message in messages:
            if self._extractable_user_facts_ispresent(message):
                extractable_facts_messages.append(message)

        extract_facts_obj: dict[str, list] = {
            "facts": []
        }
        for fact in extractable_facts_messages:
            prompt = self._format_messages(extractable_facts_messages)
            text_completion_response = self._text_completion_gbnf(memory, prompt, grammar)

            extract_facts_json_string = text_completion_response.results[0].text
            extract_facts_obj["facts"].append(json.loads(extract_facts_json_string).get("facts", []))

        return extract_facts_obj.get("facts", [])

    def _extractable_user_facts_ispresent(self, message: Message) -> bool:
        memory = CHECK_FOR_EXTRACTABLE_USER_FACTS_PROMPT
        grammar = EXTRACTABLE_FACTS_CHECK_GRAMMER
        prompt = f"{message.user_id}: {message.content}"

        text_completion_response = self._text_completion_gbnf(memory, prompt, grammar)

        match text_completion_response.results[0].text:
            case "yes":
                return True
            case "no":
                return False
            case _:
                return False

    def _text_completion_gbnf(self, memory: str, prompt: str, grammar: str) -> TextCompletionResponse:
        req = TextCompletionRequest(
            memory=self._apply_chat_template_to_system(memory),
            prompt=self._apply_chat_template_to_prompt(prompt),
            grammar=grammar
        )

        text_completion_resp = requests.post(
            self.url + "/api/v1/generate",
            json=req.model_dump()
        )

        return TextCompletionResponse.model_validate_json(text_completion_resp.text)

    def _json_to_grammar(self, schema: dict) -> str:
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

    def _format_messages(self, messages: list[Message]) -> str:
        prompt: str = ""
        for message in messages:
            prompt += f"{message.user_id}: {message.content}\n"
        prompt = prompt.rstrip("\n")
        return prompt

