import openai
from enum import Enum

# openai.api_key = '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'  # os.getenv("OPENAI_API_KEY")
# openai.api_key = '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'  # os.getenv("OPENAI_API_KEY")
openai.api_key = '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'  # os.getenv("OPENAI_API_KEY")


class TaskDifficulty(Enum):
    LOW = 'text-babbage-001'
    MEDIUM = 'text-curie-001'
    HARD = 'text-davinci-003'

    def get_model_name(self):
        return self.value


def ask(prompt: str,
        task_difficulty: TaskDifficulty = TaskDifficulty.HARD,
        max_tokens: int = 1000
        ) -> str:
    response = openai.Completion.create(
        model=task_difficulty.get_model_name(),
        prompt=prompt,
        temperature=0.5,
        max_tokens=max_tokens,
    )
    return response.choices[0].text
