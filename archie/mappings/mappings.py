from archie.models import ConversationId, Memory, TextAuthorType
from archie.persistence.entities import MemoryEntity


def to_memory_model(entity: MemoryEntity) -> Memory:
    author = TextAuthorType.User if entity.is_user_message else TextAuthorType.System
    return Memory(
        conversation_id=ConversationId(entity.conversation_id),
        moment=entity.moment,
        author=author,
        text=entity.message
    )


def to_memory_models(entities: list[MemoryEntity]) -> list[Memory]:
    return [to_memory_model(entity) for entity in entities]
