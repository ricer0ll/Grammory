import chromadb
from grammory import Grammory, Message
from mockkobold import MockKoboldClient

def test_add():
    client = chromadb.Client()
    mock_kobold_client = MockKoboldClient()
    collection = client.create_collection(name="test_add_collection")
    grammory = Grammory(collection=collection, kobold_client=mock_kobold_client)

    messages: list = [Message("test", "I'm a vegetarian and allergic to nuts.")]
    grammory.add_user_fact(messages=messages)

    result = collection.query(query_texts="What are my dietary restrictions?", where={"user_id": "test"})

    assert len(result["documents"]) == 1
    assert result["documents"][0][0] == "I'm a vegetarian and allergic to nuts."

    assert len(result["metadatas"]) == 1
    assert result["metadatas"][0][0]["user_id"] == "test"

def test_search():
    client = chromadb.Client()
    mock_kobold_client = MockKoboldClient()
    collection = client.create_collection(name="test_search_collection")
    grammory = Grammory(collection=collection, kobold_client=mock_kobold_client)

    messages: list = [
        Message("test", "I'm a vegetarian and allergic to nuts."),
        Message("test", "I play guitar.")
    ]
    grammory.add_user_fact(messages=messages)

    result = grammory.search("What are my dietary restrictions?", filters={"user_id": "test"})

    assert len(result.results) == 2
    assert result.results[0].user_id == "test"
    assert result.results[0].memory == "I'm a vegetarian and allergic to nuts."
    assert result.results[1].memory == "I play guitar." # should be lower ranked.
    assert result.results[1].distance > result.results[0].distance
