import os
import openai
from sentence_transformers import SentenceTransformer, util
import torch

from memory_entity import Memory
from storage import MemoryStorage

openai.api_key = os.getenv("OPENAI_API_KEY")


class Conversation:
    MODEL_NAME = 'text-davinci-003'
    ai_interact_counter = 0

    embedder = SentenceTransformer('all-MiniLM-L6-v2')

    def __init__(self, user_id):
        self.user_id = user_id
        self.memories: list[Memory] = []
        self.memories_embeddings = torch.Tensor([])
        self.__load_memories(user_id)

    def send_message(self, prompt: str) -> str:
        # if self.__is_question(prompt):
        #     ai_response = self.__try_ask_based_on_memories(prompt)
        # else:
        #     self.__save_prompt_as_user_memory(prompt)
        #     ai_response = self.__confirm_memory_saved(prompt)
        self.__save_prompt_as_user_memory(prompt)
        ai_response = self.__try_ask_based_on_memories(prompt)
        self.__save_ai_response_as_memory(ai_response)
        return ai_response

    def __load_memories(self, user_id):
        memories_from_db = MemoryStorage.get_memories(user_id)
        if memories_from_db and len(memories_from_db) > 0:
            self.memories = MemoryStorage.get_memories(user_id)
            memory_texts = [x.memory for x in self.memories]
            self.memories_embeddings = Conversation.embedder.encode(memory_texts, convert_to_tensor=True)

    def __try_ask_based_on_memories(self, prompt: str) -> str:
        closest_memories = self.__find_semantically_close_memories(prompt)
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
            print("-", memory.memory, f"(Score: {hit['score']:.4f}) {'' if is_really_relevant else 'DISCARDED'}")
            if is_really_relevant:
                closest_memories.append(memory)

        return closest_memories

    def __save_ai_response_as_memory(self, response: str):
        self.__save_memory(response, user_id=-1)

    def __save_prompt_as_user_memory(self, prompt: str):
        self.__save_memory(prompt, user_id=self.user_id)

    def __save_memory(self, memory: str, user_id: int):
        new_memory = MemoryStorage.add_memory(memory, user_id)
        self.memories.append(new_memory)
        new_memory_embedding = Conversation.embedder.encode(memory, convert_to_tensor=True).unsqueeze(0)
        self.memories_embeddings = torch.cat((self.memories_embeddings, new_memory_embedding))

    def __ask_based_on_memories(self, prompt: str, relevant_memories):
        the_prompt = 'You have the following memories of your conversation with user:\n'
        for memory in relevant_memories:
            memory_owner = "YOU" if memory.user_id == -1 else 'USER'
            memory_extended = f'* [{memory.moment}][FROM {memory_owner}] {memory.memory}\n'
            the_prompt += memory_extended
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
