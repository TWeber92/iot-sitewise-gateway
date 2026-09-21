from dataclasses import dataclass, field


@dataclass
class Asset:
    asset_id: str
    asset_name: str = None
    asset_properties: list = field(default_factory=list)

    def to_dict(self):
        return {'id': self.asset_id, 'name': self.asset_name}