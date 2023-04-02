from dataclasses import dataclass, asdict


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
    story: str
    data: dict
