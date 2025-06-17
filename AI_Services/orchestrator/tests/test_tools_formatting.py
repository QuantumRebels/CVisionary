from datetime import datetime
from schemas import ChunkItem
from tools import format_context_for_prompt

def test_format_context_for_prompt_logic():
    """Tests the logic for formatting retrieved chunks into a string."""
    # Arrange
    chunks = [
        ChunkItem(
            chunk_id="c1", user_id="u1", index_namespace="profile", section_id=None,
            source_type="experience", source_id="0", text="  Profile experience text.  ",
            score=0.9, created_at=datetime.utcnow()
        ),
        ChunkItem(
            chunk_id="c2", user_id="u1", index_namespace="resume_sections", section_id="skills-section",
            source_type="user_edited", source_id="0", text="User edited skills text.",
            score=0.8, created_at=datetime.utcnow()
        ),
    ]

    # Act
    formatted_string = format_context_for_prompt(chunks)

    # Assert
    # FIX: Assertions now match the actual output format from tools.py
    expected_line_1 = "- From profile (experience): Profile experience text."
    expected_line_2 = "- From resume_sections (user_edited): User edited skills text."
    
    assert expected_line_1 in formatted_string
    assert expected_line_2 in formatted_string

def test_format_context_for_prompt_with_empty_list():
    """Tests the formatter with an empty list of chunks."""
    assert format_context_for_prompt([]) == "No relevant context was found from the user's profile."