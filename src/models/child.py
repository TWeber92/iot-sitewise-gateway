import json
from dataclasses import dataclass


@dataclass
class Child:
    id: str
    name: str

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }


class ChildEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Child):
            return o.__dict__
        return json.JSONEncoder.default(self, o)