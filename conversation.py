import os
import openai
from sentence_transformers import SentenceTransformer, util
import torch

from storage import MemoryStorage

openai.api_key = os.getenv("OPENAI_API_KEY")


class Conversation:
    MODEL_NAME = 'text-davinci-003'
    ai_interact_counter = 0

    embedder = SentenceTransformer('all-MiniLM-L6-v2')

    def __init__(self, user_id):
        self.user_id = user_id
        self.memories = []
        self.memories_embeddings = torch.Tensor([])
        self.__load_memories(user_id)

    def send_message(self, prompt: str) -> str:
        if self.__is_question(prompt):
            return self.__try_ask_based_on_memories(prompt)
        else:
            self.__save_prompt_as_user_memory(prompt)
            return self.__confirm_memory_saved(prompt)

    def __load_memories(self, user_id):
        memories_from_db = MemoryStorage.get_memories(user_id)
        if memories_from_db and len(memories_from_db) > 0:
            self.memories = [x['memory'] for x in MemoryStorage.get_memories(user_id)]
            self.memories_embeddings = Conversation.embedder.encode(self.memories, convert_to_tensor=True)

    def __try_ask_based_on_memories(self, prompt: str) -> str:
        closest_memories = self.__find_semantically_close_memories(prompt)
        if len(closest_memories) == 0:
            return self.__no_memories_found(prompt)
        else:
            return self.__ask_based_on_memories(prompt, closest_memories)

    def __find_semantically_close_memories(self, prompt: str, memories_limit: int = 5):
        # Embedding of the prompt
        prompt_embedding = Conversation.embedder.encode(prompt, convert_to_tensor=True)
        # Search for memories similar to the prompt
        hits = util.semantic_search(prompt_embedding, self.memories_embeddings, top_k=memories_limit)
        hits = hits[0]

        # Collecting the similar memories
        closest_memories = []
        for hit in hits:
            hit_id = hit['corpus_id']
            memory = self.memories[hit_id]
            is_really_relevant = hit['score'] > 0.1
            print("-", memory, f"(Score: {hit['score']:.4f}) {'' if is_really_relevant else 'DISCARDED'}")
            if is_really_relevant:
                closest_memories.append(memory)

        return closest_memories

    def __save_prompt_as_user_memory(self, prompt: str):
        self.memories.append(prompt)
        new_memory_embedding = Conversation.embedder.encode(prompt, convert_to_tensor=True).unsqueeze(0)
        self.memories_embeddings = torch.cat((self.memories_embeddings, new_memory_embedding))
        MemoryStorage.add_memory(prompt, self.user_id)

    def __is_question(self, prompt: str) -> bool:
        the_prompt = f'Is it a question: "{prompt}"? ' \
                     f'Answer exactly "yes" or "no", lower-case, without punctuation.'
        response = self.__ask_ai(the_prompt)
        response = response.replace('\n', '')
        print('is_question:', response)
        return response.lower() == 'yes'

    def __no_memories_found(self, prompt: str) -> str:
        the_prompt = f'The user asks you this: "{prompt}". ' \
                     'But you haven\'t found anything related, what user might have told you earlier. ' \
                     'Answer the user only using basic general facts. ' \
                     'If it is not enough for proper answer, indicate it. ' \
                     'Use language of the users request.'
        response = self.__ask_ai(the_prompt)
        print('no_memories_found:', response)
        return response

    def __ask_based_on_memories(self, prompt: str, relevant_memories):
        the_prompt = 'The user once told you this facts:\n'
        for memory in relevant_memories:
            the_prompt += f'* {memory}\n'
        the_prompt += f'Using this information, answer the following user request: "{prompt}". ' \
                      'Don\'t make anything up, use only this info + basic general knowledge.' \
                      'Use language of the users request.'
        response = self.__ask_ai(the_prompt)
        print('answer_based_on_memories:', response)
        return response

    def __confirm_memory_saved(self, prompt: str):
        the_prompt = f'You are a personal assistant. The user just told you "{prompt}".' \
                     f'Answer as if you\'ve written it down / saved / remembered what he told you. ' \
                     'Use language of the users request.'
        response = self.__ask_ai(the_prompt)
        print('confirm_memory_saved:', response)
        return response

    def __ask_ai(self, prompt: str, max_tokens: int = 1000) -> str:
        response = openai.Completion.create(
            model=Conversation.MODEL_NAME,
            prompt=prompt,
            temperature=0.6,
            max_tokens=max_tokens,
        )
        Conversation.ai_interact_counter += 1
        print(f"OpenAI call #{Conversation.ai_interact_counter}")
        return response.choices[0].text
