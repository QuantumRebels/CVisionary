# test_chunking.py

from chunking import chunk_text, extract_text_fields

def test_chunk_text():
    """Test the text chunking logic."""
    long_text = "This is the first sentence. This is the second sentence. This is the third sentence which is a bit longer."
    # With a low word count, it should split
    chunks = chunk_text(long_text, max_words=10)
    assert len(chunks) == 2
    assert chunks[0] == "This is the first sentence. This is the second sentence."
    assert chunks[1] == "This is the third sentence which is a bit longer."

    # With a high word count, it should not split
    chunks_no_split = chunk_text(long_text, max_words=100)
    assert len(chunks_no_split) == 1

    # Test empty and whitespace text
    assert chunk_text("") == []
    assert chunk_text("   ") == []

def test_extract_text_fields():
    """Test the extraction of text from a profile dictionary."""
    profile = {
        "experience": [{"description": "exp desc"}],
        "projects": [{"description": "proj desc"}],
        "skills": ["skill1", "skill2"],
        "summary": "summary text",
        "bio": None, # Should be ignored
        "other_field": "ignore this"
    }
    fields = extract_text_fields(profile)
    texts = [f[2] for f in fields]
    assert "exp desc" in texts
    assert "proj desc" in texts
    assert "skill1, skill2" in texts
    assert "summary text" in texts
    assert len(fields) == 4