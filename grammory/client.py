import uuid
from datetime import datetime
import chromadb
from .dataclasses import Message, SearchResults, Memory
from .kobold import KoboldInterface

class Grammory:
    def __init__(self, collection: chromadb.Collection, kobold_client: KoboldInterface):
        self.collection: chromadb.Collection = collection
        self.kobold_client: KoboldInterface = kobold_client

    def add_user_fact(self, messages: list[Message]):
        if len(messages) == 0:
            return

        extracted_facts = self.kobold_client.extract_facts(messages)

        ids = [str(uuid.uuid7()) for _ in extracted_facts]
        documents = [fact for fact in extracted_facts]
        metadatas = [
            {"user_id": messages[0].user_id, "created_at": str(datetime.now())} 
            for _ in extracted_facts
        ] # we assume all user_id's per list is the same.

        self.collection.add(
            ids=ids,
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

        for ids, documents, metadatas, distances in zip(result["ids"], result["documents"], result["metadatas"], result["distances"]):
            for id, document, metadata, distance in zip(ids, documents, metadatas, distances):
                # print(id, document, metadata, distance)
                search_result_list.append(Memory(
                    id=id,
                    user_id=metadata.get("user_id", ""),
                    memory=document,
                    created_at=metadata.get("created_at", ""),
                    distance=distance
                ))

        return SearchResults(results=search_result_list)
                