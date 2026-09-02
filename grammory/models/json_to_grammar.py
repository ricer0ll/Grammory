from pydantic import BaseModel

class JsonToGrammarResponse(BaseModel):
    result: str
    success: bool