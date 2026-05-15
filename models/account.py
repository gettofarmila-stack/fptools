from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Balance:
    rub: float=0.0
    usd: float=0.0
    eur: float=0.0

@dataclass
class Profile:
    category_ids: list
    lots: list[LotInfo] = field(default_factory=list)
    reviews: list[CurReview] = field(default_factory=list)

@dataclass
class CurReview:
    text: str
    stars: int
    author: str
    item_name: str

@dataclass
class UserData:
    csrf_token: str
    user_id: str

@dataclass
class Order:
    order_id: Optional[str] = None
    order_time: Optional[str] = None
    client_name: Optional[str] = None
    price: Optional[float] = None
    status: Optional[str] = None
    name: Optional[str] = None
    category: Optional[str] = None
    review: Optional[dict] = None

@dataclass
class Review:
    text: str
    stars: int
    answer: str