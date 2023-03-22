import psycopg2
from contextlib import closing

from memory_entity import Memory


class MemoryStorage:
    @staticmethod
    def add_memory(memory: str, user_id: int, is_user_memory: bool) -> Memory:
        params = {
            'memory': memory,
            'user_id': user_id,
            'is_user_memory': is_user_memory,
        }
        with MemoryStorage.__get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO public.memories (
                        moment,
                        user_id,
                        is_user_memory,
                        memory
                    ) 
                    VALUES (
                        now(),
                        %(user_id)s,
                        %(is_user_memory)s,
                        %(memory)s
                    )
                    RETURNING
                        id,
                        moment,
                        user_id,
                        is_user_memory,
                        memory;
                """, params)
                record = cursor.fetchone()
                memory = Memory(
                    id=record[0],
                    moment=record[1],
                    user_id=record[2],
                    is_user_memory=record[3],
                    memory=record[4],
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
                        is_user_memory,
                        memory
                    FROM public.memories
                    WHERE user_id = %(user_id)s
                    ORDER BY moment;
                """, params)
                records = cursor.fetchall()
                memories = [
                    Memory(
                        id=record[0],
                        moment=record[1],
                        user_id=record[2],
                        is_user_memory=record[3],
                        memory=record[4],
                    )
                    for record in records
                ]
                return memories

    @staticmethod
    def __get_connection():
        return closing(psycopg2.connect(dbname='remi-memory', user='remi-user',
                                        password='123456', host='localhost', port=8197))
