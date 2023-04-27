from datetime import datetime, timedelta
from enum import Enum
import json

from archie.app.brain_helpers import *
import archie.external.openai_client as openai
from archie.models import Prompt, GeneratedResponse
from archie.monitoring.logging import log_function, log
from archie.persistence.entities import MemoryEntity, Story
import archie.utilities.text as text_utils
import archie.utilities.datetime_utils as dt


class PromptClass(Enum):
    NOTHING = 1
    SELECT = 2
    INSERT = 3
    UPDATE = 4
    DELETE = 5


@log_function
def build_answer_to_question(
        prompt: Prompt,
        last_memories: list[Memory],
        relevant_memories: list[Memory],
) -> GeneratedResponse:
    now = dt.to_str(datetime.now())
    now_but_later = dt.to_str(datetime.now() + timedelta(seconds=5))

    last_memories_text = prepare_last_memories_str(last_memories)
    relevant_memories_text = prepare_relevant_memories_str(relevant_memories)

    ai_prompt = f"""
Memory Assistant is a large language model trained by OpenAI.
Memory Assistant is designed to be able to answer Human's questions based on previous conversation history.
Memory Assistant is flexible and can switch language of generated response based on the last Human's message.
Memory Assistant uses his own search techniques to extract data relevant to the Human's prompt.
{relevant_memories_text}
The most recent conversation of Human and Assistant is the following.
{last_memories_text}
[{now}] Human: {prompt.text}
[{now_but_later}] Assistant:
"""
    log(ai_prompt)
    response = openai.ask(ai_prompt, task_difficulty=openai.TaskDifficulty.HARD)
    return response


@log_function
def is_question(prompt: Prompt) -> bool:
    ai_prompt = f"""Is it a question or a statement: "{prompt}"? Answer with "question" or "statement"."""
    response = openai.ask(ai_prompt, task_difficulty=openai.TaskDifficulty.HARD)
    response = text_utils.extract_phrase(response.text)
    if response == 'question':
        return True
    if response == 'statement':
        return False
    raise Exception(f'is_question: Unexpected response "{response}"')


# TODO: fit model
@log_function
def classify_prompt(prompt: Prompt) -> PromptClass:
    ai_prompt = f"""
You are NLQ processor. You convert user's natural-language prompt into a database query. First, you need to define, what operation to perform.
User prompt is: `{prompt}`.
If user tells us a fact / a statement / a piece of info we can store, reply with 'insert'.
If user asks to amend some previous information that he gave, reply with 'update'.
If user asks to delete some previous information, reply with 'delete'.
If user asks a question, where the answer implies using some previously given information, reply with 'select'.
Reply with a single word, nothing else.
"""
    response = openai.ask(ai_prompt, task_difficulty=openai.TaskDifficulty.HARD)
    response = text_utils.extract_phrase(response)
    if response == 'nothing':
        return PromptClass.NOTHING
    if response == 'select':
        return PromptClass.SELECT
    if response == 'insert':
        return PromptClass.INSERT
    if response == 'update':
        return PromptClass.UPDATE
    if response == 'delete':
        return PromptClass.DELETE
    raise Exception(f'Unexpected prompt class "{response}"')


@log_function
def generate_story_name(prompt: Prompt) -> str:
    ai_prompt = f"""
You are a text classifier, you group semantically close texts and give each group a short tag.
Give a tag to user\'s statement: "{prompt}".
Be as specific as you can, but keep it short.
"""
    response = openai.ask(ai_prompt, task_difficulty=openai.TaskDifficulty.LOW)
    response = text_utils.extract_phrase(response)
    return response


@log_function
def generate_description(prompt: Prompt) -> str:
    ai_prompt = f"""
You are a text analyzer. I give you users message, you explain it to me and describe what it is about and what user wants.  
Users message is:
{prompt}
"""
    response = openai.ask(ai_prompt, task_difficulty=openai.TaskDifficulty.HARD)
    response = text_utils.extract_phrase(response)
    return response


@log_function
def create_fact_schema(prompt: Prompt) -> str:
    ai_prompt = f"""
You are NLQ processor. You extract all useful data from user natural-language prompt and convert it into structured JSON object.
Write a JSON Typedef schema that can fit all data from user prompt: "{prompt}".
Make it brief, but keep as much useful info as you can. Don't create excessive attributes. Don't create root property.
Don't add description fields. Don't separate date and time for moment of time representation, use datetime.
Format JSON Typedef in the most compact way - without spaces.
"""
    response = openai.ask(ai_prompt)
    return response


@log_function
def explain_prompt(prompt: Prompt) -> str:
    ai_prompt = f"""
User interacts with one NLQ system which converts natural language prompts into database queries.
User prompt is "{prompt}".
Explain in a couple of sentences what user wants.
"""
    response = openai.ask(ai_prompt)
    return response


@log_function
def create_elastic_query(prompt: Prompt, story: Story) -> dict:
    ai_prompt = f"""
You are NLQ system, you convert user natural language prompts into database queries.
You are operating ElasticSearch of version 8.6.2. Data is stored in index "facts", documents have this structure:
{{ "user_id": "{story.user_id}", "story_name": "{story.name}", "data": {{}} }}
where "data" has structure described by the following Typedef:
```
{story.schema}
```
Create DSL query by this user prompt description: "{prompt}". Format query in the most compact way.
For reference: now is {datetime.now()}.
"""
    response = openai.ask(ai_prompt)
    response = text_utils.extract_json(response)
    response = json.loads(response)
    return response


@log_function
def try_create_json_by_schema(prompt: Prompt, schema: str) -> str or None:
    the_prompt = f"""
Convert user's prompt to JSON with schema described by JSON Typedef:
```
{schema}
```
User's prompt is: "{prompt}".
If you cannot fit all data from prompt into the schema, reply "NO". Otherwise return JSON object describing the prompt with given schema. Format JSON in the most compact way.
For reference: now is {datetime.now()}.
"""
    response = openai.ask(the_prompt)
    if text_utils.extract_phrase(response) == 'no':
        return None
    return text_utils.extract_json(response)
