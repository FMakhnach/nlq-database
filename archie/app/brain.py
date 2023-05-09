from datetime import datetime, timedelta
import json

from archie.app.brain_helpers import *
import archie.external.openai_client as openai
from archie.models import GeneratedResponse, QueryClass, UserQuery
from archie.monitoring.logging import log_function, log
from archie.persistence.entities import StoryEntity
import archie.utilities.text as text_utils
import archie.utilities.datetime_utils as dt


@log_function
def build_answer_to_question(
        query: UserQuery,
        last_memories: list[Memory],
        relevant_memories: list[Memory],
) -> GeneratedResponse:
    now = dt.to_str(datetime.now())
    now_but_later = dt.to_str(datetime.now() + timedelta(seconds=5))

    last_memories_text = prepare_last_memories_str(last_memories)
    # To not repeat the same messages twice
    relevant_memories_filtered = exclude_last_memories_from_relevant_memories(relevant_memories, last_memories)
    relevant_memories_text = prepare_relevant_memories_str(relevant_memories_filtered)

    prompt = f"""
Archie is a memory-oriented large language model trained by OpenAI.
Archie is designed to be able to answer Human's questions based on previous conversation history.
Archie is flexible and can switch language of generated response based on the last Human's message.
Archie uses his own search techniques to extract data relevant to the Human's message.
{relevant_memories_text}
The most recent conversation of Human and Archie is the following.
{last_memories_text}
[{now}] Human: {query.text}
[{now_but_later}] Archie:
"""
    log(prompt)
    response = openai.ask(prompt, task_difficulty=openai.TaskDifficulty.HARD)
    return response


@log_function
def generate_saved_fact_response(query: UserQuery) -> GeneratedResponse:
    prompt = f"""
Archie is a memory-oriented large language model trained by OpenAI.
Archie is designed to save information user gives to him in messages.
Archie is flexible and can switch language of generated response based on the last Human's message.
Human just told you:
```
{query.text}
```
You successfully saved this info. Reply to user briefly and affirmatively.
"""
    log(prompt)
    response = openai.ask(prompt, task_difficulty=openai.TaskDifficulty.HARD)
    return response


@log_function
def is_question(query: UserQuery) -> bool:
    prompt = f"""Is it a question or a statement: "{query.text}"? Answer with "question" or "statement"."""
    response = openai.ask(prompt, task_difficulty=openai.TaskDifficulty.HARD)
    response = text_utils.extract_phrase(response.text)
    if response == 'question':
        return True
    if response == 'statement':
        return False
    raise Exception(f'is_question: Unexpected response "{response}"')


# TODO: fit model
@log_function
def classify_query(query: UserQuery) -> QueryClass:
    if is_question(query):
        return QueryClass.ASK
    else:
        return QueryClass.ADD


#     prompt = f"""
# You are NLQ processor. You convert user's natural language message into a database query. First, you need to define, what operation to perform.
# User query is: `{query.text}`.
# If user tells us a fact / a statement / a piece of info we can store, reply with 'insert'.
# If user asks to amend some previous information that he gave, reply with 'update'.
# If user asks to delete some previous information, reply with 'delete'.
# If user asks a question, where the answer implies using some previously given information, reply with 'select'.
# Reply with a single word, nothing else.
# """
#     response = openai.ask(prompt, task_difficulty=openai.TaskDifficulty.HARD)
#     response = text_utils.extract_phrase(response.text)
#     if response == 'nothing':
#         return QueryClass.NOTHING
#     if response == 'select':
#         return QueryClass.ASK
#     if response == 'insert':
#         return QueryClass.ADD
#     if response == 'update':
#         return QueryClass.UPD
#     if response == 'delete':
#         return QueryClass.DROP
#     raise Exception(f'Unexpected query class "{response}"')


@log_function
def generate_tag(query: UserQuery) -> str:
    prompt = f"""
You are a text classifier, you group semantically close texts and give each group a short tag.
Give a tag to user\'s statement: "{query.text}".
Be as specific as you can, but keep it short.
"""
    response = openai.ask(prompt, task_difficulty=openai.TaskDifficulty.LOW)
    response_text = text_utils.extract_phrase(response.text)
    return response_text


@log_function
def generate_reference_text(query: UserQuery) -> str:
    prompt = f"""
You are a text analyzer. I give you users message, you explain it to me and describe what it is about and what user wants.  
Users message is:
{query.text}
"""
    response = openai.ask(prompt, task_difficulty=openai.TaskDifficulty.HARD)
    response_text = text_utils.extract_phrase(response.text)
    return response_text


@log_function
def create_fact_schema(query: UserQuery) -> str:
    prompt = f"""
You are NLQ processor. You extract all useful data from user natural language messages and convert it into structured JSON object.
Write a JSON Typedef schema that can fit all data from user query: "{query.text}".
Make it brief, but keep as much useful info as you can. Don't create excessive attributes. Don't create root property.
Don't add description fields. Don't separate date and time for moment of time representation, use datetime.
Format JSON Typedef in the most compact way - without spaces.
"""
    response = openai.ask(prompt)
    return response.text


@log_function
def explain_query(query: UserQuery) -> str:
    prompt = f"""
User interacts with one NLQ system which converts natural language messages into database queries.
User query is "{query.text}".
Explain in a couple of sentences what user wants.
"""
    response = openai.ask(prompt).text
    return response


@log_function
def create_elastic_query(query: UserQuery, story: StoryEntity) -> dict:
    prompt = f"""
You are NLQ system, you convert user natural language messages into database queries.
You are operating ElasticSearch of version 8.6.2. Data is stored in index "facts", documents have this structure:
{{ "conversation_id": "{story.conversation_id}", "story_id": "{story.id}", "data": {{}} }}
where "data" has structure described by the following Typedef:
```
{story.schema}
```
Create DSL query by this users message: "{query.text}". Format query in the most compact way.
For reference: now is {datetime.now()}.
"""
    response = openai.ask(prompt).text
    response = text_utils.extract_json(response)
    response = json.loads(response)
    return response


@log_function
def try_create_json_by_schema(query: UserQuery, schema: str) -> str or None:
    prompt = f"""
Convert user's message to JSON with schema described by JSON Typedef:
```
{schema}
```
User's message is: "{query.text}".
If you cannot fit all data from message into the schema, reply "NO". Otherwise return JSON object describing the prompt with given schema. Format JSON in the most compact way.
For reference: now is {datetime.now()}.
"""
    response = openai.ask(prompt).text
    if text_utils.extract_phrase(response) == 'no':
        return None
    return text_utils.extract_json(response)
