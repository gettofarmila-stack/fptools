from dataclasses import dataclass


@dataclass
class CurrentLotInfo:
    short_desc: str
    description: str
    price: float