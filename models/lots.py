from dataclasses import dataclass


@dataclass
class CurrentLotInfo:
    short_desc: str
    description: str
    price: float

@dataclass
class LotEditor:
    csrf_token: str
    form_created_at: str
    offer_id: str
    node_id: str
    location: str
    deleted: str