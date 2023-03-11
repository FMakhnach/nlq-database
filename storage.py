import psycopg2
from contextlib import closing

from memory_entity import Memory


class MemoryStorage:
    @staticmethod
    def add_memory(memory: str, user_id: int) -> Memory:
        params = {
            'message': memory,
            'user_id': user_id,
        }
        with MemoryStorage.__get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO public.memories (
                        moment,
                        user_id,
                        message
                    ) 
                    VALUES (
                        now(),
                        %(user_id)s,
                        %(message)s
                    )
                    RETURNING
                        moment,
                        user_id,
                        message;
                """, params)
                record = cursor.fetchone()
                memory = Memory(
                    moment=record[0],
                    user_id=record[1],
                    memory=record[2],
                )
                conn.commit()
                return memory

    @staticmethod
    def get_memories(user_id: int) -> list[Memory]:
        params = {
            'user_id': user_id,
        }
        with MemoryStorage.__get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        id,
                        moment,
                        user_id,
                        message
                    FROM public.memories
                    WHERE user_id = %(user_id)s;
                """, params)
                records = cursor.fetchall()
                memories = [
                    Memory(
                        moment=record[1],
                        user_id=record[2],
                        memory=record[3],
                    )
                    for record in records
                ]
                return memories

    @staticmethod
    def __get_connection():
        return closing(psycopg2.connect(dbname='remi-memory', user='remi-user',
                                        password='123456', host='localhost', port=8197))
