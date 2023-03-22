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
        ai_response = self.__write_query()  # self.__try_ask_based_on_memories(prompt)
        # self.__save_prompt_as_user_memory(prompt)
        # self.__save_ai_response_as_memory(ai_response)
        return ai_response

    def __load_memories(self, user_id):
        memories_from_db = MemoryStorage.get_memories(user_id)
        if memories_from_db and len(memories_from_db) > 0:
            self.memories = MemoryStorage.get_memories(user_id)
            memory_texts = [x.memory for x in self.memories]
            self.memories_embeddings = Conversation.embedder.encode(memory_texts, convert_to_tensor=True)

    def __try_ask_based_on_memories(self, prompt: str) -> str:
        last_memories_to_take = 5
        latest_memories = self.memories[-min(last_memories_to_take, len(self.memories)):]
        closest_memories = self.__find_semantically_close_memories(prompt)
        return self.__ask_based_on_memories(prompt, latest_memories, closest_memories)

    def __find_semantically_close_memories(self, prompt: str, memories_limit: int = 5) -> list[Memory]:
        # Embedding of the prompt
        prompt_embedding = Conversation.embedder.encode(prompt, convert_to_tensor=True)
        # Search for memories similar to the prompt
        hits = util.semantic_search(prompt_embedding, self.memories_embeddings, top_k=memories_limit)
        hits = hits[0]

        # Collecting the similar memories
        closest_memories: list[Memory] = []
        for hit in hits:
            hit_id = hit['corpus_id']
            memory = self.memories[hit_id]
            is_really_relevant = hit['score'] > 0.1
            print("-", memory.memory, f"(Score: {hit['score']:.4f}) {'' if is_really_relevant else 'DISCARDED'}")
            if is_really_relevant:
                closest_memories.append(memory)

        return closest_memories

    def __save_ai_response_as_memory(self, response: str):
        self.__save_memory(response, user_id=self.user_id, is_user_memory=False)

    def __save_prompt_as_user_memory(self, prompt: str):
        self.__save_memory(prompt, user_id=self.user_id, is_user_memory=True)

    def __save_memory(self, memory: str, user_id: int, is_user_memory: bool):
        new_memory = MemoryStorage.add_memory(memory, user_id, is_user_memory)
        self.memories.append(new_memory)
        new_memory_embedding = Conversation.embedder.encode(memory, convert_to_tensor=True).unsqueeze(0)
        self.memories_embeddings = torch.cat((self.memories_embeddings, new_memory_embedding))

    def __ask_based_on_memories(self,
                                prompt: str,
                                latest_memories: list[Memory],
                                relevant_memories: list[Memory]) -> str:
        the_prompt = f'You are a personal assistant. User asks you: "{prompt}".\n'
        if len(latest_memories) > 0:
            the_prompt += 'Your last messages with user:\n'
            for memory in reversed(latest_memories):
                memory_owner = 'USER' if memory.is_user_memory else 'YOU'
                memory_text = memory.memory.replace("\n", " ")
                memory_extended = f'* [{memory.moment}][FROM {memory_owner}] {memory_text}\n'
                the_prompt += memory_extended
        if len(relevant_memories) > 0:
            the_prompt += 'Some other relevant messages:\n'
            for memory in relevant_memories:
                memory_owner = 'USER' if memory.is_user_memory else 'YOU'
                memory_text = memory.memory.replace("\n", " ")
                memory_extended = f'* [{memory.moment}][FROM {memory_owner}] {memory_text}\n'
                the_prompt += memory_extended
        the_prompt += f'Using this information, answer user request. ' \
                      'If you don\'t have enough data to answer, indicate it. ' \
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

    def __requires_context(self, prompt: str):
        # the_prompt = f'Do you require some context (some info about user) ' \
        #              f'to properly answer this user prompt: "{prompt}"? ' \
        #              f'Answer just "yes" or "no".'
        the_prompt = f'You are a personal assistant bot with the following categories you can work with: "general questions", "notes", "laundry tracking", "shopping list". ' \
                     f'User request is: "{prompt}". If this request matches one of the categories, answer just with name of this category,. Otherwise, answer "no" and propose a category for this request with a couple of words.'
        response = self.__ask_ai(the_prompt)
        # print('confirm_memory_saved:', response)
        return response

    def __try_get_context(self, prompt: str):
        the_prompt = f"""
You are an operator of computer with AI that process user requests in following modes:
"general question": User asks a question that can be properly answered using ONLY plain facts from the Internet. It must not require any personal information about user. Example: "What is the capital of Belgium?".
"note": User enters some piece of information (possibly personal) that he wants to save and retrieve later. Example: "Sauce for spaghetti carbonara is called \"carbonara\"".
"Shopping List": User enters a list of items that he needs to buy and the AI stores it for later retrieval.

You need to process user's request: "{prompt}".
If any of this modes match user's request, answer in such manner: "YES, <mode_name>", where <mode_name> is one of the modes previously listed.
Otherwise, create a new mode that would process this request: make up a name and a description, similar to existing modes. Answer with "NO, <mode_name>: <description>".
"""
        response = self.__ask_ai(the_prompt)
        return response

    def __write_query(self):
        the_prompt = f"""
User asks you: "I just bought apples and eggs. What's left?".
You keep users data in PostgreSQL, you have the following tables:
```
CREATE TABLE shopping_list (
    id SERIAL PRIMARY KEY,
    item VARCHAR(255) NOT NULL
);

CREATE TABLE user_requests (
    id SERIAL PRIMARY KEY,
    request VARCHAR(255) NOT NULL,
    shopping_list_id INTEGER REFERENCES shopping_list(id)
);
```
Write a query to this tables to get data to answer the users request. If you need to save data, write insert/update command.
"""
        print(the_prompt)
        response = self.__ask_ai(the_prompt)
        return response

    def __create_context(self, mode_description: str = None):
        mode_description = '"Shopping List": User enters a list of items that he needs to buy and the AI stores it for later retrieval.'
        the_prompt = f"""
You will have to process user's requests with the following scenario: `{mode_description}. Example: "I need to buy apples, milk, tomatoes and eggs. Write it down."`.
Other possible usages:
- Retrieving the list of items they need to buy: "What did I need to buy?"
- Adding items to the list: "I also need to buy bread."
- Removing items from the list: "I don't need to buy tomatoes anymore."
- Updating items on the list: "I need to buy two gallons of milk."

To answer such requests, you will need to save some data to storage and then retrieve it. Write PostgreSQL expressions to create tables you will need to store and process user's requests.
        """

#         mode_description = '"Shopping List": User enters a list of items that he needs to buy and the AI stores it for later retrieval.'
#         the_prompt = f"""
# You will have to process user's requests with the following scenario: `{mode_description}. Example: "I need to buy apples, milk, tomatoes and eggs. Write it down."`.
# 1. Expand on the scenario: what other types of requests can user make potentially? Describe it briefly.
# 2. Imagine you have to keep some data from user's requests in storage. Considering your answer to p.1, write PostgreSQL expressions to create tables you will need to store and process user's data.
#         """

#         the_prompt = f"""
# You are a personal assistant that process user requests. You remember nothing by yourself, but you can user Postgresql database. You can create tables and query them to retrieve or save user information.
# You have the following tables already:
# * CREATE TABLE ShoppingList (item VARCHAR(255));
# User asked you: "I've bought apples and tomatoes, write it down.".
# If you want to execute some SQL commands, start your response with "SQL: ". If a table does not exist, you first need to create this table. You can also extend existing tables if it doesn't lead to data corruption.
# Otherwise, answer to user.
# """
        print(the_prompt)
        response = self.__ask_ai(the_prompt)
        return response

    def __ask_ai(self, prompt: str, max_tokens: int = 2000) -> str:
        response = openai.Completion.create(
            model=Conversation.MODEL_NAME,
            prompt=prompt,
            temperature=0.2,
            max_tokens=max_tokens,
        )
        # Conversation.ai_interact_counter += 1
        # print(f"OpenAI call #{Conversation.ai_interact_counter}")
        return response.choices[0].text
