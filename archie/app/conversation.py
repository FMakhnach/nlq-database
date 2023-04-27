from datetime import datetime
import json

import archie.app.brain as brain
import archie.mappings as mappings
from archie.models import ConversationId, GeneratedResponse, Memory, Prompt
from archie.monitoring.logging import log, log_wrap_function_call, log_function
import archie.persistence.facts_repository as facts_repo
import archie.persistence.memories_repository as memories_repo
import archie.persistence.stories_repository as stories_repo
import archie.persistence.entities as entities


class Conversation:

    def __init__(self, conversation_id: ConversationId):
        self.conversation_id: ConversationId = conversation_id

    @log_wrap_function_call
    def respond(self, prompt: Prompt) -> GeneratedResponse:
        request_time = datetime.now()

        response = self.generate_response(prompt)

        response_time = datetime.now()

        self.save_user_memory(prompt, request_time)
        self.save_ai_response(response, response_time)

        return response

    @log_function
    def generate_response(self, prompt: Prompt) -> GeneratedResponse:
        if brain.is_question(prompt):
            return self.answer_question(prompt)
        else:
            return self.process_statement(prompt)

    @log_function
    def answer_question(self, prompt: Prompt) -> GeneratedResponse:
        # 1. Last memories
        last_memories = self.get_last_memories()
        # 2. The most relevant memories
        relevant_memories = self.get_relevant_memories(prompt)

        response = brain.build_answer_to_question(
            prompt,
            last_memories,
            relevant_memories)

        return response

    # @log_function
    def process_statement(self, prompt: Prompt) -> GeneratedResponse:
        return GeneratedResponse(f'Successfully saved fact: {prompt}')
        # stories = self.find_relevant_stories(prompt, 0.5)
        # for story_found in sorted(stories, key=lambda x: -x.score):
        #     story = story_found.story
        #     saved_fact = self.try_save_fact(prompt, story)
        #     if saved_fact is not None:
        #         return f'Successfully saved fact: {saved_fact}'  # TODO better response
        # new_story = self.create_new_story(prompt)
        # saved_fact = self.try_save_fact(prompt, new_story)
        # if saved_fact is not None:
        #     return f'Successfully saved fact: {saved_fact}'  # TODO better response
        # else:
        #     return 'Failed to save fact'

    # @log_function
    # def answer_question_old(self, prompt: Prompt) -> str:
    #     stories = self.find_relevant_stories(prompt, threshold=0.9, try_create=False)
    #     relevant_facts = None
    #     for story_found in sorted(stories, key=lambda x: -x.score):
    #         story = story_found.story
    #         log(f'Trying story "{story.name}"')
    #         num_tries = 3
    #         for i in range(num_tries):
    #             explained_prompt = brain.explain_prompt(prompt)
    #             log(f"Explained prompt: {explained_prompt}")
    #             try:
    #                 elastic_query = brain.create_elastic_query(explained_prompt, story)
    #                 query_str = str(elastic_query).replace("'", '"')
    #                 log(f"Query is:\n{query_str}")
    #                 relevant_facts = facts_repo.search_facts(elastic_query)
    #                 break
    #             except Exception as err:
    #                 log(f'Failed to send query to elastic: {err}')
    #         if relevant_facts is not None:
    #             break
    #     if relevant_facts is None:
    #         return 'No info was found'  # TODO
    #     else:
    #         return str(relevant_facts)  # TODO
    #
    # @log_function
    # def try_save_fact(self, prompt: Prompt, story: entities.Story) -> entities.Fact or None:
    #     num_tries = 3
    #     for i in range(num_tries):
    #         fact_json = brain.try_create_json_by_schema(prompt, story.schema)
    #         if fact_json is None:
    #             continue
    #         log(f'Schema "{story.schema}" fits')
    #         log(f'Got json: "{fact_json}"')
    #         try:
    #             fact_data = json.loads(fact_json)
    #             fact = entities.Fact(
    #                 user_id=self.user_id,
    #                 story_name=story.name,
    #                 data=fact_data,
    #             )
    #             facts_repo.add_fact(fact)
    #             return fact
    #         except Exception as err:
    #             log(f'Failed to add data: {err}')
    #     return None
    #
    # @log_function
    # def find_relevant_stories(
    #         self,
    #         prompt: Prompt,
    #         threshold: float,
    #         try_create: bool = True,
    # ) -> list[entities.StorySearchResult]:
    #     prompt_short_description = brain.generate_description(prompt)
    #     relevant_stories = stories_repo.search_relevant_stories(self.user_id, prompt_short_description, threshold)
    #     if len(relevant_stories) > 0:
    #         log('Stories FOUND')
    #         return relevant_stories
    #     else:
    #         log(f'Stories not found')
    #         if try_create:
    #             new_story = self.create_new_story(prompt)
    #             stories_repo.add_story(new_story)
    #             result = entities.StorySearchResult(new_story, score=1.0)
    #             log(f'Created a new story: name="{new_story.name}", schema="{new_story.schema}".')
    #             return [result]
    #         else:
    #             return []

    @log_function
    def create_new_story(self, prompt: Prompt) -> entities.Story:
        story_name = brain.generate_story_name(prompt)
        story_description = brain.generate_description(prompt)
        schema = brain.create_fact_schema(prompt)
        story = entities.Story(
            user_id=self.conversation_id,
            name=story_name,
            description=story_description,
            prompt=prompt,
            schema=schema,
        )
        return story

    def save_user_memory(self, user_prompt: Prompt, moment: datetime):
        user_req_memory = entities.MemoryEntity(
            conversation_id=self.conversation_id.value,
            is_user_message=True,
            moment=moment,
            message=user_prompt.text.strip(),
        )
        memories_repo.add_memory(user_req_memory)

    def save_ai_response(self, ai_response: GeneratedResponse, moment: datetime):
        ai_resp_memory = entities.MemoryEntity(
            conversation_id=self.conversation_id.value,
            is_user_message=False,
            moment=moment,
            message=ai_response.text.strip(),
        )
        memories_repo.add_memory(ai_resp_memory)

    def get_last_memories(self) -> list[Memory]:
        last_memory_entities = memories_repo.get_last_memories(self.conversation_id)
        last_memories = mappings.to_memory_models(last_memory_entities)
        return last_memories

    def get_relevant_memories(self, prompt: Prompt) -> list[Memory]:
        search_result = memories_repo.search_relevant_memories(self.conversation_id, prompt)
        relevant_memory_entities = [x.memory for x in search_result]
        relevant_memories = mappings.to_memory_models(relevant_memory_entities)
        return relevant_memories
