from dataclasses import dataclass


@dataclass
class Line:
    line_name: str = None
    line_id: str = None
    line_status: int = None
    speed: int = None
    maintenance: str = None
    schedule: str = None
    machine_downtime: int = None

    def to_dict(self):
        return {
            "lineName": self.line_name,
            "lineId": self.line_id,
            "lineStatus": self.line_status,
            "speed": self.speed,
            "maintenance": self.maintenance,
            "schedule": self.schedule,
            "machineDowntime": self.machine_downtime
        }