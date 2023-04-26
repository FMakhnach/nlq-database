from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ConvertableToDict:
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Memory(ConvertableToDict):
    user_id: str
    is_users: bool
    moment: datetime
    memory: str

    def __str__(self):
        user = 'USER' if self.is_users else 'YOU'
        return f'[{self.moment.strftime("%B %d, %Y %H:%M:%S")}] {user}: "{self.memory}"'


@dataclass
class MemorySearchResult:
    memory: Memory
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
