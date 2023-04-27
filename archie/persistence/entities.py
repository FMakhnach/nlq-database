from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ConvertableToDict:
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MemoryEntity(ConvertableToDict):
    conversation_id: str
    is_user_message: bool
    moment: datetime
    message: str


@dataclass
class MemorySearchResult:
    memory: MemoryEntity
    score: float


@dataclass
class Story(ConvertableToDict):
    conversation_id: str
    key: str
    reference: str
    message: str
    schema: str


@dataclass
class StorySearchResult:
    story: Story
    score: float


@dataclass
class Fact(ConvertableToDict):
    conversation_id: str
    story_key: str
    data: dict
