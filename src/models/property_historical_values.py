from dataclasses import dataclass, field
from typing import List


@dataclass
class PropertyHistoricalValues:
    asset: dict
    property_name: str
    property_id: str
    start_time: int
    end_time: int
    qualities: List[str]
    time_ordering: str
    max_results: int
    values: List[dict] = field(default_factory=list)

    @classmethod
    def from_query_params(cls, asset, query_params):
        return cls(
            asset=asset.to_dict(),
            property_name=query_params.property_name,
            property_id=query_params.property_id,
            start_time=query_params.start_date,
            end_time=query_params.end_date,
            qualities=query_params.qualities,
            time_ordering=query_params.time_ordering,
            max_results=query_params.max_results,
        )

    def to_dict(self):
        return {
            "asset": self.asset,
            "propertyName": self.property_name,
            "propertyId": self.property_id,
            "startTime": self.start_time,
            "endTime": self.end_time,
            "qualities": self.qualities,
            "timeOrdering": self.time_ordering,
            "maxResults": self.max_results,
            "values": self.values,
        }
