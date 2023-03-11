from datetime import datetime
from dataclasses import dataclass


@dataclass
class Memory:
    moment: datetime
    user_id: str
    memory: str
