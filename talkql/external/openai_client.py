from datetime import datetime
from enum import Enum
import openai
import os

from talkql.models import GeneratedResponse
import talkql.persistence.openai_calls_logs_repository as logs

openai.api_key = os.getenv("OPENAI_API_KEY")


class TaskDifficulty(Enum):
    LOW = 'text-babbage-001'
    MEDIUM = 'text-curie-001'
    HARD = 'text-davinci-003'

    def get_model_name(self):
        return self.value


def ask(prompt: str,
        task_difficulty: TaskDifficulty = TaskDifficulty.HARD,
        max_tokens: int = 500,
        ) -> GeneratedResponse:
    params = {
        "model": task_difficulty.get_model_name(),
        "prompt": prompt,
        "temperature": 0.1,
        "max_tokens": max_tokens,
    }
    response = openai.Completion.create(**params)
    response_text = response.choices[0].text
    logs.add({'moment': datetime.now(), 'params': params, 'response': response_text})
    return GeneratedResponse(text=response_text)
