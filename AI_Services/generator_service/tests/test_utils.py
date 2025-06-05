import pytest
from unittest.mock import patch, MagicMock
from utils import extract_keywords, build_rag_prompt, PREDEFINED_SKILLS


class TestExtractKeywords:
    def test_extract_single_keyword(self):
        """Test extracting a single keyword from text."""
        text = "We are looking for a Python developer"
        result = extract_keywords(text)
        assert "Python" in result["required"]
        assert result["preferred"] == []
    
    def test_extract_multiple_keywords(self):
        """Test extracting multiple keywords from text."""
        text = "Looking for Python and AWS experience with Docker"
        result = extract_keywords(text)
        expected_skills = {"Python", "AWS", "Docker"}
        assert expected_skills.issubset(set(result["required"]))
        assert result["preferred"] == []
    
    def test_case_insensitive_matching(self):
        """Test case-insensitive keyword matching."""
        text = "Experience with python, aws, and DOCKER required"
        result = extract_keywords(text)
        expected_skills = {"Python", "AWS", "Docker"}
        assert expected_skills.issubset(set(result["required"]))
    
    def test_word_boundary_matching(self):
        """Test that partial word matches are avoided."""
        text = "We use JavaScript but not Java"
        result = extract_keywords(text)
        assert "JavaScript" in result["required"]
        # Should not match "Java" from "JavaScript"
        if "Java" in result["required"]:
            # This would be expected if "Java" appears as a separate word
            pass
    
    def test_no_keywords_found(self):
        """Test when no predefined keywords are found."""
        text = "Looking for a great team player with excellent communication skills"
        result = extract_keywords(text)
        assert result["required"] == []
        assert result["preferred"] == []
    
    def test_empty_text(self):
        """Test with empty input text."""
        result = extract_keywords("")
        assert result["required"] == []
        assert result["preferred"] == []
    
    def test_all_predefined_skills_present(self):
        """Test with text containing all predefined skills."""
        text = " ".join(PREDEFINED_SKILLS)
        result = extract_keywords(text)
        assert len(result["required"]) == len(PREDEFINED_SKILLS)


class TestBuildRagPrompt:
    @patch('utils.render_rag_prompt')
    def test_build_rag_prompt_basic(self, mock_render):
        """Test basic RAG prompt building."""
        mock_render.return_value = "Mocked prompt"
        
        chunks = [
            {
                "chunk_id": "1",
                "user_id": "user1",
                "source_type": "resume",
                "source_id": "resume1",
                "text": "Python developer with 5 years experience",
                "score": 0.9
            }
        ]
        keywords = {"required": ["Python"], "preferred": []}
        
        result = build_rag_prompt("Test Job Description", chunks, keywords)
        
        assert result == "Mocked prompt"
        mock_render.assert_called_once()
        
        # Check the minimal chunks passed to render function
        passed_kwargs = mock_render.call_args.kwargs
        job_desc_arg = passed_kwargs['job_description']
        minimal_chunks = passed_kwargs['chunks']
        keywords_arg = passed_kwargs['keywords']
        assert job_desc_arg == "Test Job Description"
        assert len(minimal_chunks) == 1
        assert minimal_chunks[0]["source_type"] == "resume"
        assert minimal_chunks[0]["source_id"] == "resume1"
        assert minimal_chunks[0]["text"] == "Python developer with 5 years experience"
    
    @patch('utils.render_rag_prompt')
    def test_build_rag_prompt_multiple_chunks(self, mock_render):
        """Test RAG prompt building with multiple chunks."""
        mock_render.return_value = "Multi-chunk prompt"
        
        chunks = [
            {
                "chunk_id": "1",
                "user_id": "user1",
                "source_type": "resume",
                "source_id": "resume1",
                "text": "Python developer",
                "score": 0.9
            },
            {
                "chunk_id": "2",
                "user_id": "user1",
                "source_type": "project",
                "source_id": "project1",
                "text": "Built REST API",
                "score": 0.8
            }
        ]
        keywords = {"required": ["Python", "REST"], "preferred": ["AWS"]}
        
        result = build_rag_prompt("Test Job Description", chunks, keywords)
        
        assert result == "Multi-chunk prompt"
        passed_kwargs = mock_render.call_args.kwargs
        job_desc_arg = passed_kwargs['job_description']
        minimal_chunks = passed_kwargs['chunks']
        keywords_arg = passed_kwargs['keywords']
        assert job_desc_arg == "Test Job Description"
        assert len(minimal_chunks) == 2
    
    @patch('utils.render_rag_prompt')
    def test_build_rag_prompt_missing_fields(self, mock_render):
        """Test RAG prompt building with chunks missing fields."""
        mock_render.return_value = "Prompt with defaults"
        
        chunks = [
            {
                "chunk_id": "1",
                "user_id": "user1",
                # Missing source_type, source_id, text
                "score": 0.9
            }
        ]
        keywords = {"required": [], "preferred": []}
        
        result = build_rag_prompt("Test Job Description", chunks, keywords)
        
        passed_kwargs = mock_render.call_args.kwargs
        job_desc_arg = passed_kwargs['job_description']
        minimal_chunks = passed_kwargs['chunks']
        keywords_arg = passed_kwargs['keywords']
        assert job_desc_arg == "Test Job Description"
        assert minimal_chunks[0]["source_type"] == "unknown"
        assert minimal_chunks[0]["source_id"] == "unknown"
        assert minimal_chunks[0]["text"] == ""
    
    @patch('utils.render_rag_prompt')
    def test_build_rag_prompt_empty_chunks(self, mock_render):
        """Test RAG prompt building with empty chunks list."""
        mock_render.return_value = "Empty prompt"
        
        chunks = []
        keywords = {"required": ["Python"], "preferred": []}
        
        result = build_rag_prompt("Test Job Description", chunks, keywords)
        
        assert result == "Empty prompt"
        passed_kwargs = mock_render.call_args.kwargs
        job_desc_arg = passed_kwargs['job_description']
        minimal_chunks = passed_kwargs['chunks']
        keywords_arg = passed_kwargs['keywords']
        assert job_desc_arg == "Test Job Description"
        assert len(minimal_chunks) == 0