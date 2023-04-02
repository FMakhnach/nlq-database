import brain
import json
import elastic
import logging as log
from models import Story, StorySearchResult, Fact

log.basicConfig(filename='logs.log', level=log.INFO)


class Conversation:

    def __init__(self, user_id):
        self.user_id = user_id

    def send_message(self, prompt: str) -> str:
        log.info(f'>> Received prompt: {prompt}')
        if brain.is_question(prompt):
            log.info('> QUESTION')
            return self.answer_question(prompt)
        else:
            log.info('> STATEMENT')
            return self.process_statement(prompt)

    def answer_question(self, prompt: str) -> str:
        stories = self.find_relevant_stories(prompt, threshold=0.9)
        relevant_facts = None
        for story_found in sorted(stories, key=lambda x: -x.score):
            story = story_found.story
            log.info(f'Trying story "{story.story_name}"')
            num_tries = 3
            for i in range(num_tries):
                explained_prompt = brain.explain_prompt(prompt)
                log.info(f"Explained prompt: {explained_prompt}")
                try:
                    elastic_query = brain.create_elastic_query(explained_prompt, story)
                    log.info(f"Query is:\n{elastic_query}")
                    relevant_facts = elastic.search_facts(elastic_query)
                    break
                except Exception as err:
                    log.warning(f'Failed to send query to elastic: {err}')
            if relevant_facts is not None:
                break
        if relevant_facts is None:
            return 'No info was found'  # TODO
        else:
            return str(relevant_facts)  # TODO

    def process_statement(self, prompt: str) -> str:
        stories = self.find_relevant_stories(prompt, 0.9)
        for story_found in sorted(stories, key=lambda x: -x.score):
            story = story_found.story
            log.info(f'Trying story "{story.story_name}"')
            saved_fact = self.try_save_fact(prompt, story)
            if saved_fact is not None:
                return f'Successfully saved fact: {saved_fact}'  # TODO better response
        log.info('SUITABLE STORY WAS NOT FOUND. Generating new.')
        new_story = self.create_new_story(prompt)
        log.info(f'Generated story: {new_story}')
        saved_fact = self.try_save_fact(prompt, new_story)
        if saved_fact is not None:
            return f'Successfully saved fact: {saved_fact}'  # TODO better response
        else:
            return 'Failed to save fact'

    def try_save_fact(self, prompt: str, story: Story) -> Fact or None:
        num_tries = 3
        for i in range(num_tries):
            fact_json = brain.try_create_json_by_schema(prompt, story.fact_schema)
            if fact_json is None:
                continue
            log.info(f'Schema "{story.fact_schema}" fits')
            log.info(f'Got json: "{fact_json}"')
            try:
                fact_data = json.loads(fact_json)
                fact = Fact(
                    user_id=self.user_id,
                    story=story.story_name,
                    data=fact_data,
                )
                elastic.add_fact(fact)
                return fact
            except Exception as err:
                log.warning(f'Failed to add data: {err}')
        return None

    def find_relevant_stories(self, prompt: str, threshold: float) -> list[StorySearchResult]:
        log.info(f'> Start looking for story for "{prompt}"...')
        relevant_stories = elastic.search_relevant_stories(self.user_id, prompt, threshold)
        if len(relevant_stories) > 0:
            log.info('Stories FOUND')
            return relevant_stories
        else:
            log.info(f'Stories not found')
            new_story = self.create_new_story(prompt)
            elastic.add_story(new_story)
            result = StorySearchResult(new_story, score=1.0)
            log.info(f'Created a new story: name="{new_story.story_name}", schema="{new_story.fact_schema}".')
            return [result]

    def create_new_story(self, prompt: str) -> Story:
        story_name = brain.get_short_description(prompt)
        schema = brain.create_fact_schema(prompt)
        story = Story(
            story_name=story_name,
            user_id=self.user_id,
            prompt=prompt,
            fact_schema=schema,
        )
        return story
