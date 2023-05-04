from datetime import datetime
import json

import archie.app.brain as brain
import archie.mappings as mappings
from archie.models import ConversationId, GeneratedResponse, Memory, QueryClass, UserQuery
from archie.monitoring.logging import log, log_wrap_function_call, log_function
import archie.persistence.facts_repository as facts_repo
import archie.persistence.memories_repository as memories_repo
import archie.persistence.stories_repository as stories_repo
import archie.persistence.entities as entities


class Conversation:

    def __init__(self, conversation_id: ConversationId):
        self.conversation_id: ConversationId = conversation_id

    @log_wrap_function_call
    def respond(self, query: UserQuery) -> GeneratedResponse:
        request_time = datetime.now()

        response = self.generate_response(query)

        response_time = datetime.now()

        self.save_user_memory(query, request_time)
        self.save_ai_response(response, response_time)

        return response

    @log_function
    def generate_response(self, query: UserQuery) -> GeneratedResponse:
        query_class = query.operation_hint if query.operation_hint else brain.classify_query(query)
        if query_class == QueryClass.ASK:
            return self.answer_question(query)
        elif query_class == QueryClass.ADD:
            return self.process_statement(query)
        elif query_class == QueryClass.UPD:
            return GeneratedResponse(f'Unsupported operation: {query.operation_hint}')  # TODO
        elif query_class == QueryClass.DROP:
            return GeneratedResponse(f'Unsupported operation: {query.operation_hint}')  # TODO
        elif query_class == QueryClass.NOTHING:
            return GeneratedResponse(f'Unsupported operation: {query.operation_hint}')  # TODO
        else:
            return GeneratedResponse(f'Unsupported operation: {query.operation_hint}')  # TODO

    @log_function
    def answer_question(self, query: UserQuery) -> GeneratedResponse:
        # 1. Last memories
        last_memories = self.get_last_memories()
        # 2. The most relevant memories
        relevant_memories = self.get_relevant_memories(query)

        response = brain.build_answer_to_question(
            query,
            last_memories,
            relevant_memories)

        return response

    @log_function
    def process_statement(self, query: UserQuery) -> GeneratedResponse:
        stories = self.get_or_create_relevant_stories(query, 0.7)
        saved_fact = None
        for story_found in sorted(stories, key=lambda x: -x.score):
            story = story_found.story
            saved_fact = self.try_extract_and_save_fact(query, story)
            if saved_fact is not None:
                break
        if saved_fact is None:
            new_story = self.create_new_story(query)
            self.try_extract_and_save_fact(query, new_story)
        response = brain.generate_saved_fact_response(query)
        return response

    # @log_function
    # def answer_question_old(self, query: UserQuery) -> str:
    #     stories = self.find_relevant_stories(query, threshold=0.9, try_create=False)
    #     relevant_facts = None
    #     for story_found in sorted(stories, key=lambda x: -x.score):
    #         story = story_found.story
    #         log(f'Trying story "{story.name}"')
    #         num_tries = 3
    #         for i in range(num_tries):
    #             explained_query = brain.explain_query(query)
    #             log(f"Explained query: {explained_query}")
    #             try:
    #                 elastic_query = brain.create_elastic_query(explained_query, story)
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

    @log_function
    def get_or_create_relevant_stories(
            self,
            query: UserQuery,
            threshold: float,
            try_create: bool = True,
    ) -> list[entities.StorySearchResult]:
        reference_text = query.text  # brain.generate_reference_text(query)
        relevant_stories = stories_repo.search_relevant_stories(
            self.conversation_id,
            reference_text,
            threshold)
        if len(relevant_stories) > 0:
            log('Stories FOUND')
            return relevant_stories
        else:
            log(f'Stories not found')
            if not try_create:
                return []
            new_story = self.create_new_story(query)
            log(f'Created a new story: name="{new_story.key}", schema="{new_story.schema}".')
            search_result = entities.StorySearchResult(new_story, score=1.0)
            return [search_result]

    @log_function
    def create_new_story(self, query: UserQuery) -> entities.Story:
        story_tag = brain.generate_tag(query)
        story_reference = query.text  # TODO better? brain.generate_reference_text(query)
        schema = brain.create_fact_schema(query)
        story = entities.Story(
            conversation_id=self.conversation_id.value,
            key=story_tag,
            reference=story_reference,
            message=query.text,
            schema=schema,
        )
        stories_repo.add_story(story)
        return story

    @log_function
    def try_extract_and_save_fact(self, query: UserQuery, story: entities.Story) -> entities.Fact or None:
        fact_json = brain.try_create_json_by_schema(query, story.schema)
        if fact_json is None:
            return None
        log(f'Schema "{story.schema}" fits')
        log(f'Got json: "{fact_json}"')
        try:
            fact_data = json.loads(fact_json)
            fact = entities.Fact(
                conversation_id=self.conversation_id.value,
                story_key=story.key,
                data=fact_data,
            )
            facts_repo.add_fact(fact)
            return fact
        except Exception as err:
            log(f'Failed to add data: {err}')
        return None

    def save_user_memory(self, user_query: UserQuery, moment: datetime):
        user_req_memory = entities.MemoryEntity(
            conversation_id=self.conversation_id.value,
            is_user_message=True,
            moment=moment,
            message=user_query.text.strip(),
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

    def get_relevant_memories(self, query: UserQuery) -> list[Memory]:
        search_result = memories_repo.search_relevant_memories(self.conversation_id, query.text)
        relevant_memory_entities = [x.memory for x in search_result]
        relevant_memories = mappings.to_memory_models(relevant_memory_entities)
        return relevant_memories
