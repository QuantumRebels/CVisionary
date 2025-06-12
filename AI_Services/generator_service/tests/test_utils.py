# tests/test_utils.py

from datetime import datetime
from schemas import ChunkItem
from utils import format_context_for_prompt

def test_format_context_for_prompt():
    """Tests the logic for formatting retrieved chunks into a string."""
    # Arrange: Create mock chunks from different namespaces
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

    # Act
    formatted_string = format_context_for_prompt(chunks)

    # Assert
    assert "--- CONTEXT FROM PROFESSIONAL PROFILE ---" in formatted_string
    assert "Source: Profile section 'experience'" in formatted_string
    assert "Profile experience text." in formatted_string
    assert "--- CONTEXT FROM OTHER USER-EDITED SECTIONS ---" in formatted_string
    assert "Source: User-edited section 'skills'" in formatted_string
    assert "User edited skills text." in formatted_string

def test_format_context_for_prompt_empty():
    """Tests the formatter with an empty list of chunks."""
    assert format_context_for_prompt([]) == "No relevant context found."