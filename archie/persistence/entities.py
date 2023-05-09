from dataclasses import dataclass, asdict
from datetime import datetime
from uuid import UUID, uuid4 as uuid


@dataclass
class ConvertableToDict:
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MemoryEntity(ConvertableToDict):
    conversation_id: str
    is_user_text: bool
    text: str

    id: UUID = uuid()
    created_at: datetime = datetime.now()


@dataclass
class MemorySearchResult:
    memory: MemoryEntity
    score: float


@dataclass
class StoryEntity(ConvertableToDict):
    conversation_id: str
    reference_text: str
    schema: str

    id: UUID = uuid()
    created_at: datetime = datetime.now()


@dataclass
class StorySearchResult:
    story: StoryEntity
    score: float


@dataclass
class FactEntity(ConvertableToDict):
    conversation_id: str
    story_id: UUID
    data: dict

    id: UUID = uuid()
    created_at: datetime = datetime.now()
