from datetime import datetime
import json

import archie.app.brain as brain
from archie.monitoring.logging import log, log_wrap_function_call, log_function
import archie.persistence.facts_repository as facts_repo
import archie.persistence.memories_repository as memories_repo
import archie.persistence.stories_repository as stories_repo
import archie.persistence.entities as entities


class Conversation:

    def __init__(self, user_id):
        self.user_id = user_id

    @log_wrap_function_call
    @log_function
    def send_message(self, prompt: str) -> str:
        last_memories = memories_repo.get_last_memories(self.user_id)

        # if brain.is_question(prompt):
        #     response = self.answer_question(prompt)
        # else:
        #     response = self.process_statement(prompt)

        last_memories = sorted(last_memories, key=lambda x: x.moment)
        response = brain.respond(prompt, last_memories)

        self.save_memories(prompt, response)

        return response

    def save_memories(self, user_prompt: str, ai_response: str):
        user_req_memory = entities.Memory(
            user_id=str(self.user_id),
            is_users=True,
            moment=datetime.now(),
            memory=user_prompt,
        )
        memories_repo.add_memory(user_req_memory)

        ai_resp_memory = entities.Memory(
            user_id=str(self.user_id),
            is_users=True,
            moment=datetime.now(),
            memory=ai_response,
        )
        memories_repo.add_memory(ai_resp_memory)

    @log_function
    def answer_question(self, prompt: str) -> str:
        stories = self.find_relevant_stories(prompt, threshold=0.9, try_create=False)
        relevant_facts = None
        for story_found in sorted(stories, key=lambda x: -x.score):
            story = story_found.story
            log(f'Trying story "{story.name}"')
            num_tries = 3
            for i in range(num_tries):
                explained_prompt = brain.explain_prompt(prompt)
                log(f"Explained prompt: {explained_prompt}")
                try:
                    elastic_query = brain.create_elastic_query(explained_prompt, story)
                    query_str = str(elastic_query).replace("'", '"')
                    log(f"Query is:\n{query_str}")
                    relevant_facts = facts_repo.search_facts(elastic_query)
                    break
                except Exception as err:
                    log(f'Failed to send query to elastic: {err}')
            if relevant_facts is not None:
                break
        if relevant_facts is None:
            return 'No info was found'  # TODO
        else:
            return str(relevant_facts)  # TODO

    @log_function
    def process_statement(self, prompt: str) -> str:
        stories = self.find_relevant_stories(prompt, 0.5)
        for story_found in sorted(stories, key=lambda x: -x.score):
            story = story_found.story
            saved_fact = self.try_save_fact(prompt, story)
            if saved_fact is not None:
                return f'Successfully saved fact: {saved_fact}'  # TODO better response
        new_story = self.create_new_story(prompt)
        saved_fact = self.try_save_fact(prompt, new_story)
        if saved_fact is not None:
            return f'Successfully saved fact: {saved_fact}'  # TODO better response
        else:
            return 'Failed to save fact'

    @log_function
    def try_save_fact(self, prompt: str, story: entities.Story) -> entities.Fact or None:
        num_tries = 3
        for i in range(num_tries):
            fact_json = brain.try_create_json_by_schema(prompt, story.schema)
            if fact_json is None:
                continue
            log(f'Schema "{story.schema}" fits')
            log(f'Got json: "{fact_json}"')
            try:
                fact_data = json.loads(fact_json)
                fact = entities.Fact(
                    user_id=self.user_id,
                    story_name=story.name,
                    data=fact_data,
                )
                facts_repo.add_fact(fact)
                return fact
            except Exception as err:
                log(f'Failed to add data: {err}')
        return None

    @log_function
    def find_relevant_stories(
            self,
            prompt: str,
            threshold: float,
            try_create: bool = True,
    ) -> list[entities.StorySearchResult]:
        prompt_short_description = brain.generate_description(prompt)
        relevant_stories = stories_repo.search_relevant_stories(self.user_id, prompt_short_description, threshold)
        if len(relevant_stories) > 0:
            log('Stories FOUND')
            return relevant_stories
        else:
            log(f'Stories not found')
            if try_create:
                new_story = self.create_new_story(prompt)
                stories_repo.add_story(new_story)
                result = entities.StorySearchResult(new_story, score=1.0)
                log(f'Created a new story: name="{new_story.name}", schema="{new_story.schema}".')
                return [result]
            else:
                return []

    @log_function
    def create_new_story(self, prompt: str) -> entities.Story:
        story_name = brain.generate_story_name(prompt)
        story_description = brain.generate_description(prompt)
        schema = brain.create_fact_schema(prompt)
        story = entities.Story(
            user_id=self.user_id,
            name=story_name,
            description=story_description,
            prompt=prompt,
            schema=schema,
        )
        return story
