from dataclasses import dataclass
from typing import List


@dataclass
class QueryParams:
    asset_id: str
    property_name: str
    property_id: str
    start_date: int
    end_date: int
    qualities: List[str]
    time_ordering: str
    next_token: str = None
    max_results: int = None