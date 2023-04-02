from dataclasses import dataclass, asdict
from enum import Enum


class PromptClass(Enum):
    NOTHING = 1
    SELECT = 2
    INSERT = 3
    UPDATE = 4
    DELETE = 5


@dataclass
class ConvertableToDict:
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Story(ConvertableToDict):
    story_name: str
    user_id: str
    prompt: str
    fact_schema: str


@dataclass
class StorySearchResult:
    story: Story
    score: float


@dataclass
class Fact(ConvertableToDict):
    user_id: str
    story_name: str
    data: dict
