from archie.models import ConversationId, Memory, TextAuthorType
from archie.persistence.entities import MemoryEntity


def to_memory_model(entity: MemoryEntity) -> Memory:
    author = TextAuthorType.User if entity.is_user_text else TextAuthorType.System
    return Memory(
        id=entity.id,
        created_at=entity.created_at,
        conversation_id=ConversationId(entity.conversation_id),
        author=author,
        text=entity.text,
    )


def to_memory_models(entities: list[MemoryEntity]) -> list[Memory]:
    return [to_memory_model(entity) for entity in entities]
