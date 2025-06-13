# tests/test_tools_formatting.py

from datetime import datetime
from schemas import ChunkItem
from tools import format_context_for_prompt

def test_format_context_for_prompt_logic():
    """Tests the logic for formatting retrieved chunks into a string."""
    chunks = [
        ChunkItem(
            chunk_id="c1", user_id="u1", index_namespace="profile", section_id=None,
            source_type="experience", source_id="0", text="Profile experience text.",
            score=0.9, created_at=datetime.utcnow()
        ),
        ChunkItem(
            chunk_id="c2", user_id="u1", index_namespace="resume_sections", section_id="skills",
            source_type="user_edited", source_id="0", text="User edited skills text.",
            score=0.8, created_at=datetime.utcnow()
        ),
    ]

    formatted_string = format_context_for_prompt(chunks)

    assert "- From Profile (experience): Profile experience text." in formatted_string
    assert "- From another resume section ('skills'): User edited skills text." in formatted_string

def test_format_context_for_prompt_with_empty_list():
    """Tests the formatter with an empty list of chunks."""
    assert format_context_for_prompt([]) == "No relevant context was found from the user's profile."