from datetime import datetime
from enum import Enum
import json

from archie.persistence.entities import Memory, Story
import archie.external.openai_client as openai
from archie.monitoring.logging import log_function
import archie.utilities.text as text_utils


class PromptClass(Enum):
    NOTHING = 1
    SELECT = 2
    INSERT = 3
    UPDATE = 4
    DELETE = 5


def build_response(
        prompt: str,
        last_memories: list[Memory] or None,
        relevant_memories: list[Memory] or None,
        additional_data: str or None,
) -> str:
    ai_prompt = f"""
"""
    if last_memories is None or len(last_memories) == 0:
        ai_prompt += 'You have no recorded history of your conversation, so consider this is the first message.'
    else:
        ai_prompt += 'You have the following information recorded:'

        memories_chat = ''.join(['\n* ' + str(m) for m in last_memories])
        ai_prompt += f"\n- Your previous conversation:\n```{memories_chat}\n```"""

        if relevant_memories is not None and len(relevant_memories) > 0:
            other_memories = ''.join(['\n* ' + str(m) for m in relevant_memories])
            ai_prompt += f"\n- Some other relevant messages:\n```{other_memories}\n```"""

        if additional_data is not None and additional_data.strip() != '':
            ai_prompt += f"\n- Other relevant information:\n{additional_data}\n"""

        ai_prompt += f'\nUsing this information, answer the following user request: "{prompt}".'

    ai_prompt += f' Do NOT make things up. You don\'t have to use recalled data, but use it if it suits response. Use language of the prompt!\nFor the reference: now is {datetime.now()}.'
    response = openai.ask(ai_prompt, task_difficulty=openai.TaskDifficulty.HARD)
    return response


@log_function
def is_question(prompt: str) -> bool:
    ai_prompt = f"""Is it a question or a statement: "{prompt}"? Answer with "question" or "statement"."""
    response = openai.ask(ai_prompt, task_difficulty=openai.TaskDifficulty.HARD)
    response = text_utils.extract_phrase(response)
    if response == 'question':
        return True
    if response == 'statement':
        return False
    raise Exception(f'is_question: Unexpected response "{response}"')


# TODO: fit model
@log_function
def classify_prompt(prompt: str) -> PromptClass:
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
def generate_story_name(prompt: str) -> str:
    ai_prompt = f"""
You are a text classifier, you group semantically close texts and give each group a short tag.
Give a tag to user\'s statement: "{prompt}".
Be as specific as you can, but keep it short.
"""
    response = openai.ask(ai_prompt, task_difficulty=openai.TaskDifficulty.LOW)
    response = text_utils.extract_phrase(response)
    return response


@log_function
def generate_description(prompt: str) -> str:
    ai_prompt = f"""
You are a text analyzer. I give you users message, you explain it to me and describe what it is about and what user wants.  
Users message is:
{prompt}
"""
    response = openai.ask(ai_prompt, task_difficulty=openai.TaskDifficulty.HARD)
    response = text_utils.extract_phrase(response)
    return response


@log_function
def create_fact_schema(prompt: str) -> str:
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
def explain_prompt(prompt: str) -> str:
    ai_prompt = f"""
User interacts with one NLQ system which converts natural language prompts into database queries.
User prompt is "{prompt}".
Explain in a couple of sentences what user wants.
"""
    response = openai.ask(ai_prompt)
    return response


@log_function
def create_elastic_query(prompt: str, story: Story) -> dict:
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
def try_create_json_by_schema(prompt: str, schema: str) -> str or None:
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
