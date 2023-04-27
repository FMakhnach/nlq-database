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
    user_id: str
    name: str
    description: str
    prompt: str
    schema: str


@dataclass
class StorySearchResult:
    story: Story
    score: float


@dataclass
class Fact(ConvertableToDict):
    user_id: str
    story_name: str
    data: dict
