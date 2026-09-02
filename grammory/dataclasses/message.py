from dataclasses import dataclass

@dataclass
class Message:
    user_id: str
    content: str