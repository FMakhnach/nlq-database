from talkql.ml.embedder import EMBEDDER_MODEL, EMBEDDER_DIMS
import migrations

# migrations.create_memories_index(EMBEDDER_MODEL, EMBEDDER_DIMS)
# migrations.create_openai_calls_logs_index()
migrations.create_stories_index(EMBEDDER_MODEL, EMBEDDER_DIMS)
# migrations.create_facts_index()
