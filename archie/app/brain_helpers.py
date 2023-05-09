from archie.models import Memory, TextAuthorType
import archie.utilities.datetime_utils as dt


def prepare_last_memories_str(last_memories: list[Memory]) -> str or None:
    last_memories_text = None
    if last_memories is not None and len(last_memories) > 0:
        # Sort memories ascending by moment
        last_memories = sorted(last_memories, key=lambda x: x.moment)
        # Concatenate memories to single string
        last_memories_text = concat_memories(last_memories)
    return last_memories_text


def exclude_last_memories_from_relevant_memories(
        relevant_memories: list[Memory],
        last_memories: list[Memory]
) -> list[Memory]:
    last_memories_ids = set(obj.id for obj in last_memories)
    return [memory for memory in relevant_memories if memory.id not in last_memories_ids]


def prepare_relevant_memories_str(relevant_memories: list[Memory]) -> str or None:
    if relevant_memories is not None and len(relevant_memories) > 0:
        other_memories = ''.join(['\n' + memory_to_dialog_str(m) for m in relevant_memories])
        relevant_memories_text = f"""
Archie recalled some previous Human messages, most relevant to the last Human's request:
```
{other_memories}
```
"""
    else:
        relevant_memories_text = """
In his long-term memory Archie found nothing corresponding to the last Human's request.
"""

    return relevant_memories_text


def concat_memories(memories: list[Memory]) -> str:
    return ''.join(['\n' + memory_to_dialog_str(m) for m in memories])


def memory_to_dialog_str(memory: Memory):
    moment_str = dt.to_str(memory.created_at)
    author_str = text_author_type_to_dialog_str(memory.author)
    return f'[{moment_str}] {author_str}: {memory.text}'


def text_author_type_to_dialog_str(author_type: TextAuthorType):
    match author_type:
        case TextAuthorType.User:
            return 'Human'
        case TextAuthorType.System:
            return 'Archie'
        case _:
            raise ValueError(f'Unknown TextAuthorType: {author_type}')
