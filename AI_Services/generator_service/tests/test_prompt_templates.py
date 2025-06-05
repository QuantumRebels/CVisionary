import pytest
from prompt_templates import render_rag_prompt, RAG_PROMPT_TEMPLATE


class TestRenderRagPrompt:
    def test_render_basic_prompt(self):
        """Test rendering basic RAG prompt with single chunk."""
        chunks = [
            {
                "source_type": "resume",
                "source_id": "resume1",
                "text": "Python developer with 5 years experience"
            }
        ]
        keywords = {
            "required": ["Python", "AWS"],
            "preferred": ["Docker"]
        }
        
        result = render_rag_prompt("Test Job Description", chunks, keywords)
        
        assert "Python, AWS" in result
        assert "Docker" in result
        assert "resume (ID: resume1)" in result
        assert "Python developer with 5 years experience" in result
        assert "Generate 5 concise bullet points" in result
    
    def test_render_multiple_chunks(self):
        """Test rendering RAG prompt with multiple chunks."""
        chunks = [
            {
                "source_type": "resume",
                "source_id": "resume1",
                "text": "Python developer"
            },
            {
                "source_type": "project",
                "source_id": "project1",
                "text": "Built REST API"
            }
        ]
        keywords = {
            "required": ["Python"],
            "preferred": []
        }
        
        result = render_rag_prompt("Test Job Description", chunks, keywords)
        
        assert "top 2 relevant user passages" in result
        assert "resume (ID: resume1)" in result
        assert "project (ID: project1)" in result
        assert "Python developer" in result
        assert "Built REST API" in result
    
    def test_render_empty_skills(self):
        """Test rendering with empty skill lists."""
        chunks = [
            {
                "source_type": "resume",
                "source_id": "resume1",
                "text": "General experience"
            }
        ]
        keywords = {
            "required": [],
            "preferred": []
        }
        
        result = render_rag_prompt("Test Job Description", chunks, keywords)
        
        assert "The job requires: ." in result
        assert "Preferred skills: ." in result
        assert "General experience" in result
    
    def test_render_empty_chunks(self):
        """Test rendering with empty chunks list."""
        chunks = []
        keywords = {
            "required": ["Python"],
            "preferred": ["AWS"]
        }
        
        result = render_rag_prompt("Test Job Description", chunks, keywords)
        
        assert "Python" in result
        assert "AWS" in result
        assert "top 0 relevant user passages" in result
        assert "Generate 5 concise bullet points" in result
    
    def test_render_special_characters(self):
        """Test rendering with special characters in text."""
        chunks = [
            {
                "source_type": "resume",
                "source_id": "resume1",
                "text": "Python & AWS \"expert\" with 100% success rate"
            }
        ]
        keywords = {
            "required": ["Python & AWS"],
            "preferred": []
        }
        
        result = render_rag_prompt("Test Job Description", chunks, keywords)
        
        assert "Python & AWS \"expert\" with 100% success rate" in result
        assert "Python & AWS" in result
    
    def test_template_structure(self):
        """Test that the template contains all required sections."""
        assert "The job requires:" in RAG_PROMPT_TEMPLATE
        assert "Preferred skills:" in RAG_PROMPT_TEMPLATE
        assert "Here are the top" in RAG_PROMPT_TEMPLATE
        assert "relevant user passages:" in RAG_PROMPT_TEMPLATE
        assert "Generate 5 concise bullet points" in RAG_PROMPT_TEMPLATE
        assert "maximum 20 words each" in RAG_PROMPT_TEMPLATE