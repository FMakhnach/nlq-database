from datetime import datetime
import json
from models import Story
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


def get_short_description(prompt: str) -> str:
    ai_prompt = f'Describe user\'s prompt with a few words (from one to five): "{prompt}"'
    response = ai.ask(ai_prompt, task_difficulty=ai.TaskDifficulty.LOW)
    response = utils.extract_phrase(response)
    return response


def create_fact_schema(prompt: str) -> str:
    ai_prompt = f"""
You are NLQ processor. You extract data from user natural-language prompt and convert it into structured JSON objects that hold all the info from prompt and that can be used for searching later.
Write a JSON Typedef schema using YAML that can fit all data from user prompt: "{prompt}". Make it brief, but keep as much useful info as you can. Don't add description fields.
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
{{ "user_id": "{story.user_id}", "story": "{story.story_name}", "data": {{}} }}
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
