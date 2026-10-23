import os
from grammory import Message, kobold
from dotenv import load_dotenv

def test_kobold():
    load_dotenv()
    llm_host_addr = os.getenv("LLM_HOST_ADDRESS")

    mock_kobold_client = kobold.KoboldCppClient(url=llm_host_addr)

    messages: list = [
        Message("test", "I'm a vegetarian and allergic to nuts."),
        Message("test", "I play guitar."),
        Message("general", "I'm allergic to fruits.")
    ]
    
    extracted_facts = mock_kobold_client.extract_facts(messages)

    assert len(extracted_facts) > 0

