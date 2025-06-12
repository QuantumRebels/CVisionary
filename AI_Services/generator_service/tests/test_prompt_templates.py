# tests/test_prompt_templates.py

from prompt_templates import (
    FULL_RESUME_TEMPLATE,
    SECTION_REWRITE_TEMPLATE,
)

def test_full_resume_template_rendering():
    """
    Tests that the full resume template renders all placeholders correctly.
    """
    # Arrange
    mock_data = {
        "job_description": "A job for a Python developer.",
        "profile_context": "User has 5 years of Python experience.",
    }

    # Act
    rendered_prompt = FULL_RESUME_TEMPLATE.render(**mock_data)

    # Assert
    # FIX: Make assertions less brittle to whitespace and formatting
    assert mock_data["job_description"] in rendered_prompt
    assert mock_data["profile_context"] in rendered_prompt
    assert "JOB DESCRIPTION" in rendered_prompt
    assert "RELEVANT CONTEXT FROM USER'S PROFILE" in rendered_prompt
    assert "Return your response as a single, valid JSON object" in rendered_prompt

def test_section_rewrite_template_conditional_logic():
    """
    Tests the conditional blocks within the section rewrite template.
    """
    base_data = {
        "job_description": "A job for a project manager.",
        "relevant_context": "User has managed large projects.",
    }

    # Case 1: With existing_text
    data_with_text = {**base_data, "section_id": "summary", "existing_text": "Old summary."}
    prompt1 = SECTION_REWRITE_TEMPLATE.render(**data_with_text)
    assert "CURRENT SECTION CONTENT" in prompt1
    assert "Old summary." in prompt1

    # Case 2: Without existing_text
    data_without_text = {**base_data, "section_id": "summary", "existing_text": None}
    prompt2 = SECTION_REWRITE_TEMPLATE.render(**data_without_text)
    assert "CURRENT SECTION CONTENT" not in prompt2

    # Case 3: section_id is 'experience'
    data_experience = {**base_data, "section_id": "experience"}
    prompt3 = SECTION_REWRITE_TEMPLATE.render(**data_experience)
    assert "**SECTION TO REWRITE:** experience" in prompt3
    assert "1. Focus exclusively on rewriting the \"experience\" section." in prompt3

    # Case 4: section_id is 'skills'
    data_skills = {**base_data, "section_id": "skills"}
    prompt4 = SECTION_REWRITE_TEMPLATE.render(**data_skills)
    assert "**SECTION TO REWRITE:** skills" in prompt4
    assert "1. Focus exclusively on rewriting the \"skills\" section." in prompt4

    # Case 5: section_id is 'summary'
    data_summary = {**base_data, "section_id": "summary"}
    prompt5 = SECTION_REWRITE_TEMPLATE.render(**data_summary)
    assert "**SECTION TO REWRITE:** summary" in prompt5
    assert "1. Focus exclusively on rewriting the \"summary\" section." in prompt5

    # Case 6: Ensure the output format specifies the correct section_id
    prompt6 = SECTION_REWRITE_TEMPLATE.render(**data_summary)
    assert '"summary": "A rewritten, impactful professional summary' in prompt6