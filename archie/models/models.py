from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID


class QueryClass(Enum):
    NOTHING = 1
    ASK = 2
    ADD = 3
    UPD = 4
    DROP = 5

    @staticmethod
    def from_str(label: str | None):
        if label is None:
            return None
        label_lower = label.lower()
        for enum_member in QueryClass.__members__.values():
            if enum_member.name.lower() == label_lower:
                return enum_member
        return None


@dataclass
class UserQuery:
    text: str
    operation_hint: QueryClass | None = None


@dataclass
class GeneratedResponse:
    text: str


@dataclass
class ConversationId:
    value: str


class TextAuthorType(Enum):
    User = 1,
    System = 2,


@dataclass
class Memory:
    id: UUID
    created_at: datetime
    conversation_id: ConversationId
    author: TextAuthorType
    text: str
