from datetime import datetime
import json
from models import Story, PromptClass
import openai_client as ai
import utils


def is_question(prompt: str) -> bool:
    ai_prompt = f"""Is it a question or a statement: "{prompt}"? Answer with "question" or "statement"."""
    response = ai.ask(ai_prompt, task_difficulty=ai.TaskDifficulty.HARD)
    response = utils.extract_phrase(response)
    if response == 'question':
        return True
    if response == 'statement':
        return False
    raise Exception(f'is_question: Unexpected response "{response}"')


# TODO: fit model
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
    response = ai.ask(ai_prompt, task_difficulty=ai.TaskDifficulty.HARD)
    response = utils.extract_phrase(response)
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


def get_short_description(prompt: str) -> str:
    ai_prompt = f"""
You are a text classifier, you group semantically close texts and give each group a short tag.
Give a tag to user\'s statement: "{prompt}".
"""
    response = ai.ask(ai_prompt, task_difficulty=ai.TaskDifficulty.LOW)
    response = utils.extract_phrase(response)
    return response


def create_fact_schema(prompt: str) -> str:
    ai_prompt = f"""
You are NLQ processor. You extract data from user natural-language prompt and convert it into structured JSON objects that hold all the info from prompt and that can be used for searching later.
Write a JSON Typedef schema using YAML that can fit all data from user prompt: "{prompt}".
Make it brief, but keep as much useful info as you can. Don't create excessive attributes. Don't create root property.
Don't add description fields.
Prefer datetime for moment of time representation.
"""
    response = ai.ask(ai_prompt)
    return response


def explain_prompt(prompt: str) -> str:
    ai_prompt = f"""
User interacts with one NLQ system which converts natural language prompts into database queries.
User prompt is "{prompt}".
Explain in a couple of sentences what user wants.
"""
    response = ai.ask(ai_prompt)
    return response


def create_elastic_query(prompt: str, story: Story) -> dict:
    ai_prompt = f"""
You are NLQ system, you convert user natural language prompts into database queries.
You are operating ElasticSearch of version 8.6.2. Data is stored in index "facts", documents have this structure:
{{ "user_id": "{story.user_id}", "story_name": "{story.story_name}", "data": {{}} }}
where "data" has structure described by the following Typedef:
```
{story.fact_schema}
```
Create DSL query by this user prompt description: "{prompt}". Format query in the most compact way.
For reference: now is {datetime.now()}.
"""
    response = ai.ask(ai_prompt)
    response = utils.extract_json(response)
    response = json.loads(response)
    return response


def try_create_json_by_schema(prompt: str, schema: str) -> str or None:
    the_prompt = f"""
Convert user's prompt to JSON with schema described by JSON Typedef (YAML):
```
{schema}
```
User's prompt is: "{prompt}".
If you cannot fit all data from prompt into the schema, reply "NO". Otherwise return JSON object describing the prompt with given schema. Format JSON in the most compact way.
For reference: now is {datetime.now()}.
"""
    response = ai.ask(the_prompt)
    if utils.extract_phrase(response) == 'no':
        return None
    return utils.extract_json(response)
