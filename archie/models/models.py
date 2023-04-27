from dataclasses import dataclass
from datetime import datetime
from enum import Enum


@dataclass
class UserQuery:
    text: str


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
    conversation_id: ConversationId
    moment: datetime
    author: TextAuthorType
    text: str
