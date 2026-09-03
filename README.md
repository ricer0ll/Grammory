# Grammory

Grammory augments AI agents, assistants, and chatbots with an efficient and powerful memory layer, enabling personalized AI interactions. It helps AI remember user preferences and information, continuously learn, and stay in context with the user.

## Features

- **Persistent memory** — stores and retrieves user preferences, facts, and context across sessions.
- **Efficient retrieval** — powered by [ChromaDB](https://www.trychroma.com/) as the underlying vector store for fast semantic search.
- **Grammar-constrained output** — uses GBNF grammars to force the LLM to consistently produce valid JSON, removing the need for output parsing/retry logic.
- **Works on any LLM** — including small, quantized local models, as long as they run under [KoboldCpp](https://github.com/LostRuins/koboldcpp) with GBNF grammar support.
- **Lightweight integration** — designed to be dropped into existing agent/chatbot pipelines with minimal setup.

## How It Works

Grammory sits between your application and your LLM, intercepting relevant turns to extract, store, and recall memories.

1. Conversation turns are passed to Grammory.
2. Grammory prompts the LLM (via KoboldCpp) to extract memory-worthy information, using a GBNF grammar to guarantee valid, structured JSON output.
3. Extracted memories are embedded and stored in ChromaDB.
4. On future turns, relevant memories are retrieved via semantic search and injected back into context.

<!-- EXAMPLE: Basic usage snippet goes here -->

```python
import chromadb
from grammory import Grammory, Message
from grammory.kobold import KoboldClient

client = chromadb.Client()
kobold_client = KoboldClient()
collection = client.create_collection(name="test_collection")
grammory = Grammory(collection=collection, kobold_client=kobold_client)

messages: list = [
    Message("riceroll", "I'm studying computer science at Portland State University."),
    Message("riceroll", "I've been getting really into playing piano lately."),
    Message("riceroll", "I usually spend my weekends playing video games with friends.")
]

grammory.add_user_fact(messages=messages)
search_result = grammory.search("what does riceroll usually do?")
print(search_result.results)
```


## Installation

<!-- TODO: add installation instructions -->

```bash
pip install git+https://github.com/ricer0ll/Grammory.git
```

## Requirements

- [KoboldCpp](https://github.com/LostRuins/koboldcpp) with GBNF grammar support enabled
- [ChromaDB](https://www.trychroma.com/)
- Python 3.11+

## Grammory vs. mem0ai

Both Grammory and [mem0ai](https://github.com/mem0ai/mem0) aim to give LLM applications a persistent, personalized memory layer, but they differ significantly in how they achieve reliable output and which models they support.

| | **Grammory** | **mem0ai** |
|---|---|---|
| Structured output method | GBNF grammar-constrained generation — guarantees valid JSON every time | Relies on the model's own instruction-following ability to produce valid JSON |
| Model compatibility | Works on **any** LLM, including small quantized local models | Effectively requires large, capable models (e.g., Claude, GPT-4/ChatGPT) to reliably follow JSON formatting instructions |
| Backend runtime | [KoboldCpp](https://github.com/LostRuins/koboldcpp) (with GBNF support) | Typically cloud-hosted large-model APIs |
| Vector store | ChromaDB | Configurable (varies by provider) |
| Local / offline use | Yes — designed for local inference | Limited, depends on model provider |

**The key difference:** mem0ai depends on large, instruction-tuned models to reliably return well-formed JSON, which means it's effectively limited to frontier models like Claude or ChatGPT. Grammory instead uses GBNF grammars to constrain generation at the token level, forcing valid JSON output regardless of model size. This means Grammory works consistently even on small, quantized models, as long as they're served through KoboldCpp with GBNF grammar support, making it viable for fully local, low-resource, or offline setups where mem0ai would struggle.