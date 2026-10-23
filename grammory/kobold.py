import requests
import json
from .llm_client import LLMClient
from .dataclasses import Message, Memory
from .models import (
    TextCompletionRequest, 
    TextCompletionResponse, 
    JsonToGrammarResponse
)
from .prompts import (
    EXTRACT_FACT_SYSTEM_PROMPT, CHECK_FOR_EXTRACTABLE_USER_FACTS_PROMPT
)
from .grammar import (
    EXTRACT_FACTS_JSON_SCHEMA, 
    EXTRACTABLE_FACTS_CHECK_GRAMMER
)

BOS_TOKEN = "{{[INPUT]}}"
EOS_TOKEN = "{{[OUTPUT]}}"
SYSTEM_BOS_TOKEN = "{{[SYSTEM]}}"

class KoboldCppClient(LLMClient):
    def __init__(self, url: str = "http://127.0.0.1:5001", api_key: str | None = None):
        self.url = url
        self.api_key = api_key

    def extract_facts(self, messages: list[Message]) -> list[str]:
        system_prompt = EXTRACT_FACT_SYSTEM_PROMPT
        grammar = self._json_to_grammar(EXTRACT_FACTS_JSON_SCHEMA)

        relevant_messages = [
            message for message in messages
            if self._extractable_user_facts_ispresent(message)
        ]

        all_facts: list[str] = []
        for message in relevant_messages:
            prompt = f"{message.user_id}: {message.content}"
            response = self._text_completion_gbnf(system_prompt, prompt, grammar)

            facts_json = response.results[0].text
            all_facts.extend(json.loads(facts_json).get("facts", []))

        return all_facts

    def _extractable_user_facts_ispresent(self, message: Message) -> bool:
        system_prompt = CHECK_FOR_EXTRACTABLE_USER_FACTS_PROMPT
        grammar = EXTRACTABLE_FACTS_CHECK_GRAMMER
        prompt = f"{message.user_id}: {message.content}"

        response = self._text_completion_gbnf(system_prompt, prompt, grammar)

        return response.results[0].text == "yes"

    def _text_completion_gbnf(self, memory: str, prompt: str, grammar: str) -> TextCompletionResponse:
        request = TextCompletionRequest(
            memory=self._apply_chat_template_to_system(memory),
            prompt=self._apply_chat_template_to_prompt(prompt),
            grammar=grammar
        )

        headers = {}
        if self.api_key:
            headers["Authorization"] = "Bearer " + self.api_key

        response = requests.post(
            self.url + "/api/v1/generate",
            json=request.model_dump(),
            headers=headers
        )

        return TextCompletionResponse.model_validate_json(response.text)

    def _json_to_grammar(self, schema: dict) -> str:
        response = requests.post(
            self.url + "/api/extra/json_to_grammar",
            json=schema
        )

        parsed_response = JsonToGrammarResponse.model_validate_json(response.text)
        return parsed_response.result

    def _apply_chat_template_to_prompt(self, prompt: str) -> str:
        return BOS_TOKEN + prompt + EOS_TOKEN

    def _apply_chat_template_to_system(self, memory: str) -> str:
        return SYSTEM_BOS_TOKEN + memory

    def _format_messages(self, messages: list[Message]) -> str:
        lines = [f"{message.user_id}: {message.content}" for message in messages]
        return "\n".join(lines)