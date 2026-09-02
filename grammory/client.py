import uuid
from datetime import datetime
import chromadb
from .dataclasses import Message, SearchResults, Memory

class Grammory:
    def __init__(self, collection: chromadb.Collection):
        self.collection: chromadb.Collection = collection

    def add(self, messages: list[Message]):

        documents = [message.content for message in messages]
        metadatas = [
            {"user_id": message.user_id, "created_at": str(datetime.now())} 
            for message in messages
        ]

        self.collection.add(
            ids=str(uuid.uuid7()),
            documents=documents,
            metadatas=metadatas
        )

    def search(self, query: str, filters: dict[str, str], n_results: int=3) -> SearchResults:
        search_result_list: list[Memory] = []

        result = self.collection.query(
            query_texts=query,
            where=filters,
            n_results=n_results
        )

        for ids, documents, metadatas in zip(result["ids"], result["documents"], result["metadatas"]):
            for id, document, metadata in zip(ids, documents, metadatas):
                print(id, document, metadata)
                search_result_list.append(Memory(
                    id=id,
                    user_id=metadata.get("user_id", ""),
                    memory=document,
                    created_at=metadata.get("created_at", "")
                ))

        return SearchResults(results=search_result_list)
                