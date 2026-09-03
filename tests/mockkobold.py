import json
from grammory.kobold import KoboldInterface, Message, BOS_TOKEN, SYSTEM_BOS_TOKEN, EOS_TOKEN
from grammory.models.text_completion import TextCompletionRequest, TextCompletionResponse
from grammory.prompts import (
    CHECK_FOR_EXTRACTABLE_USER_FACTS_PROMPT,
    EXTRACT_FACT_SYSTEM_PROMPT
)
from grammory.grammar import (
    EXTRACT_FACTS_JSON_SCHEMA, 
    EXTRACTABLE_FACTS_CHECK_GRAMMER
)

class MockKoboldClient(KoboldInterface):
    def __init__(self, url="http://127.0.0.1:5001"):
        self.url = url

    def extract_facts(self, messages: list[Message]) -> list[str]:
        grammar = self._json_to_grammar(EXTRACT_FACTS_JSON_SCHEMA)
        memory = EXTRACT_FACT_SYSTEM_PROMPT
        extractable_facts_messages: list[Message] = []

        for message in messages:
            if self._extractable_user_facts_ispresent(message):
                extractable_facts_messages.append(message)

        prompt = self._format_messages(extractable_facts_messages)

        return [message.content for message in messages]

    def _extractable_user_facts_ispresent(self, message: Message) -> bool:
        memory = CHECK_FOR_EXTRACTABLE_USER_FACTS_PROMPT
        grammar = EXTRACTABLE_FACTS_CHECK_GRAMMER
        prompt = message.content

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

        if grammar == EXTRACTABLE_FACTS_CHECK_GRAMMER:
            return TextCompletionResponse(results=[{"text": "yes"}])

        return TextCompletionResponse(
            results=[{"text": json.dumps({"facts": ["test"]})}]
        )

    def _json_to_grammar(self, schema: dict) -> str:
        return "char ::= [^\"\\\\\\x7F\\x00-\\x1F] | [\\\\] ([\"\\\\bfnrt] | \"u\" [0-9a-fA-F]{4})\nfacts ::= \"[\" space (string (\",\" space string)*)? space \"]\"\nfacts-kv ::= \"\\\"facts\\\"\" space \":\" space facts\nroot ::= \"{\" space facts-kv space \"}\"\nspace ::= | \" \" | \"\\n\"{1,2} [ \\t]{0,20}\nstring ::= \"\\\"\" char* \"\\\"\""

    def _apply_chat_template_to_prompt(self, prompt: str) -> str:
        return BOS_TOKEN + prompt + EOS_TOKEN

    def _apply_chat_template_to_system(self, memory: str) -> str:
        return SYSTEM_BOS_TOKEN + memory

    def _format_messages(self, messages: list[Message]) -> str:
        prompt: str = ""
        for message in messages:
            prompt += message.content + "\n"
        prompt = prompt.rstrip("\n")
        return prompt