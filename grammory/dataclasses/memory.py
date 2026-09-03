from dataclasses import dataclass

@dataclass
class Memory:
    id: str
    user_id: str
    memory: str
    created_at: str
    distance: str