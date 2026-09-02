import chromadb
from grammory import Grammory
from grammory.dataclasses import Message

def test_add():
    client = chromadb.Client()
    collection = client.create_collection(name="test_add_collection")
    grammory = Grammory(collection=collection)

    messages: list = [Message("test", "I'm a vegetarian and allergic to nuts.")]
    grammory.add(messages=messages)

    result = collection.query(query_texts="What are my dietary restrictions?", where={"user_id": "test"})

    assert len(result["documents"]) == 1
    assert result["documents"][0][0] == "I'm a vegetarian and allergic to nuts."

    assert len(result["metadatas"]) == 1
    assert result["metadatas"][0][0]["user_id"] == "test"

def test_search():
    client = chromadb.Client()
    collection = client.create_collection(name="test_search_collection")
    grammory = Grammory(collection=collection)

    messages: list = [Message("test", "I'm a vegetarian and allergic to nuts.")]
    grammory.add(messages=messages)

    result = grammory.search("What are my dietary restrictions?", filters={"user_id": "test"})

    assert len(result.results) != 0
    assert result.results[0].user_id == "test"
    assert result.results[0].memory == "I'm a vegetarian and allergic to nuts."