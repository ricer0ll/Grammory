from mockkobold import MockKoboldClient
from grammory import Message

def test_kobold():
    mock_kobold_client = MockKoboldClient()

    messages: list = [
        Message("test", "I'm a vegetarian and allergic to nuts."),
        Message("test", "I play guitar."),
        Message("general", "I'm allergic to fruits.")
    ]
    
    extracted_facts = mock_kobold_client.extract_facts(messages)

    assert len(extracted_facts) > 0

