from dataclasses import dataclass
from .memory import Memory

@dataclass
class SearchResults:
    results: list[Memory]