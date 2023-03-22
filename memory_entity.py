from datetime import datetime
from dataclasses import dataclass


@dataclass
class Memory:
    id: int
    moment: datetime
    user_id: str
    is_user_memory: bool
    memory: str
