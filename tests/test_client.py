import os
import chromadb
from dotenv import load_dotenv
from grammory import Grammory, Message, kobold

load_dotenv()
LLM_HOST_ADDRESS = os.getenv("LLM_HOST_ADDRESS", "http://127.0.0.1:5001")

DIETARY_KEYWORDS = ("vegetarian", "nut", "allerg", "diet")

def test_add():
    client = chromadb.Client()
    kobold_client = kobold.KoboldCppClient(url=LLM_HOST_ADDRESS)
    collection = client.create_collection(name="test_add_collection")
    grammory = Grammory(collection=collection, kobold_client=kobold_client)

    messages: list = [Message("test", "I'm a vegetarian and allergic to nuts.")]
    grammory.add_user_fact(messages=messages)

    # the LLM may split one message into several facts, so only require at least one
    stored = collection.get()
    assert len(stored["documents"]) >= 1
    assert all(metadata["user_id"] == "test" for metadata in stored["metadatas"])

def test_search():
    client = chromadb.Client()
    kobold_client = kobold.KoboldCppClient(url=LLM_HOST_ADDRESS)
    collection = client.create_collection(name="test_search_collection")
    grammory = Grammory(collection=collection, kobold_client=kobold_client)

    messages: list = [
        Message("test", "I'm a vegetarian and allergic to nuts."),
        Message("test", "I play guitar.")
    ]
    grammory.add_user_fact(messages=messages)

    result = grammory.search("What are my dietary restrictions?", filters={"user_id": "test"}, n_results=3)

    # exact fact count depends on how the LLM splits the messages
    assert 1 <= len(result.results) <= 3
    assert all(memory.user_id == "test" for memory in result.results)
    assert [memory.distance for memory in result.results] == sorted(memory.distance for memory in result.results)
    assert any(keyword in result.results[0].memory.lower() for keyword in DIETARY_KEYWORDS)

def test_search_filters_by_user():
    client = chromadb.Client()
    kobold_client = kobold.KoboldCppClient(url=LLM_HOST_ADDRESS)
    collection = client.create_collection(name="test_search_filter_collection")
    grammory = Grammory(collection=collection, kobold_client=kobold_client)

    grammory.add_user_fact(messages=[Message("test", "I'm a vegetarian and allergic to nuts.")])
    grammory.add_user_fact(messages=[Message("other", "I'm allergic to shellfish.")])

    result = grammory.search("What are my dietary restrictions?", filters={"user_id": "other"})

    assert len(result.results) >= 1
    assert all(memory.user_id == "other" for memory in result.results)
