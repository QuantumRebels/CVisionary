import pytest
from unittest.mock import patch

from feature_extractor import (
    extract_required_keywords, 
    identify_missing_keywords, 
    PREDEFINED_SKILLS
)

class TestPredefinedSkills:
    """Test the predefined skills list"""
    
    def test_predefined_skills_not_empty(self):
        """Test that predefined skills list is not empty"""
        assert len(PREDEFINED_SKILLS) > 0
    
    def test_predefined_skills_contains_common_skills(self):
        """Test that predefined skills contains expected common skills"""
        expected_skills = ["Python", "Java", "JavaScript", "React", "AWS", "Docker"]
        
        for skill in expected_skills:
            assert skill in PREDEFINED_SKILLS
    
    def test_predefined_skills_no_duplicates(self):
        """Test that predefined skills has no duplicates"""
        assert len(PREDEFINED_SKILLS) == len(set(PREDEFINED_SKILLS))
    
    def test_predefined_skills_proper_casing(self):
        """Test that skills have proper casing"""
        # Check some specific cases
        assert "JavaScript" in PREDEFINED_SKILLS  # Not "javascript"
        assert "Node.js" in PREDEFINED_SKILLS     # Proper formatting
        assert "C++" in PREDEFINED_SKILLS         # Special characters
        assert "C#" in PREDEFINED_SKILLS          # Special characters

class TestExtractRequiredKeywords:
    """Test the extract_required_keywords function"""
    
    def test_extract_basic_skills(self):
        """Test extraction of basic skills from job description"""
        job_desc = "We need a Python developer with React experience and AWS knowledge."
        
        result = extract_required_keywords(job_desc)
        
        assert "Python" in result
        assert "React" in result
        assert "AWS" in result
    
    def test_extract_case_insensitive(self):
        """Test case-insensitive skill extraction"""
        job_desc = "Looking for python, REACT, and aws experience."
        
        result = extract_required_keywords(job_desc)
        
        assert "Python" in result
        assert "React" in result
        assert "AWS" in result
    
    def test_extract_with_word_boundaries(self):
        """Test that extraction respects word boundaries"""
        job_desc = "We need JavaScript experience, not Java or script kidding."
        
        result = extract_required_keywords(job_desc)
        
        assert "JavaScript" in result
        assert "Java" in result  # Should match "Java" separately
        # Should not match partial words
    
    def test_extract_special_characters(self):
        """Test extraction of skills with special characters"""
        job_desc = "Experience with C++ and C# programming languages required."
        
        result = extract_required_keywords(job_desc)
        
        assert "C++" in result
        assert "C#" in result
    
    def test_extract_multiple_occurrences(self):
        """Test that skills are not duplicated when mentioned multiple times"""
        job_desc = "Python developer needed. Strong Python skills required. Python experience essential."
        
        result = extract_required_keywords(job_desc)
        
        # Should only appear once
        python_count = result.count("Python")
        assert python_count == 1
    
    def test_extract_from_complex_text(self):
        """Test extraction from complex job description"""
        job_desc = """
        Senior Full Stack Developer Position
        
        Requirements:
        - 5+ years of Python development experience
        - Strong knowledge of Django and Flask frameworks
        - Frontend experience with React.js and JavaScript
        - Database experience with PostgreSQL and MySQL
        - Cloud experience with AWS (EC2, S3, Lambda)
        - Containerization with Docker and Kubernetes
        - Version control with Git
        - Experience with REST API and GraphQL
        - Agile/Scrum methodologies
        
        Nice to have:
        - TypeScript knowledge
        - Redis caching
        - Jenkins CI/CD
        """
        
        result = extract_required_keywords(job_desc)
        
        expected_skills = [
            "Python", "Django", "Flask", "React", "JavaScript", 
            "PostgreSQL", "MySQL", "AWS", "Docker", "Kubernetes", 
            "Git", "REST API", "GraphQL", "Agile", "TypeScript", 
            "Redis", "Jenkins"
        ]
        
        for skill in expected_skills:
            assert skill in result, f"Expected skill '{skill}' not found in result"
    
    def test_extract_empty_input(self):
        """Test extraction from empty job description"""
        result = extract_required_keywords("")
        assert result == []
    
    def test_extract_none_input(self):
        """Test extraction from None input"""
        result = extract_required_keywords(None)
        assert result == []
    
    def test_extract_no_matching_skills(self):
        """Test extraction when no predefined skills are mentioned"""
        job_desc = "We need someone with great communication skills and teamwork abilities."
        
        result = extract_required_keywords(job_desc)
        assert result == []
    
    def test_extract_with_punctuation(self):
        """Test extraction when skills are surrounded by punctuation"""
        job_desc = "Skills: Python, React.js, AWS; Docker (containerization), Node.js!"
        
        result = extract_required_keywords(job_desc)
        
        assert "Python" in result
        assert "React" in result
        assert "AWS" in result
        assert "Docker" in result
        assert "Node.js" in result
    
    def test_extract_error_handling(self):
        """Test error handling in extraction"""
        # This should not raise an exception
        result = extract_required_keywords("Some invalid unicode: \x00\x01")
        assert isinstance(result, list)

class TestIdentifyMissingKeywords:
    """Test the identify_missing_keywords function"""
    
    def test_identify_basic_missing(self):
        """Test basic missing keyword identification"""
        required = ["Python", "React", "AWS", "Docker"]
        resume = "I have experience with Python and React development."
        
        result = identify_missing_keywords(required, resume)
        
        assert "AWS" in result
        assert "Docker" in result
        assert "Python" not in result
        assert "React" not in result
    
    def test_identify_case_insensitive(self):
        """Test case-insensitive missing keyword identification"""
        required = ["Python", "React", "AWS"]
        resume = "Experience with PYTHON and react development."
        
        result = identify_missing_keywords(required, resume)
        
        assert "AWS" in result
        assert "Python" not in result
        assert "React" not in result

    def test_identify_all_keywords_present(self):
        """Test when all required keywords are present in the resume."""
        required = ["Python", "React"]
        resume = "I am proficient in Python and React."
        result = identify_missing_keywords(required, resume)
        assert result == []

    def test_identify_no_keywords_present(self):
        """Test when none of the required keywords are present in the resume."""
        required = ["Java", "Spring", "SQL"]
        resume = "I have experience with Python and Django."
        result = identify_missing_keywords(required, resume)
        assert "Java" in result
        assert "Spring" in result
        assert "SQL" in result
        assert len(result) == 3

    def test_identify_empty_resume(self):
        """Test when the resume text is empty."""
        required = ["Python", "React"]
        resume = ""
        result = identify_missing_keywords(required, resume)
        assert "Python" in result
        assert "React" in result
        assert len(result) == 2

    def test_identify_empty_required_list(self):
        """Test when the list of required keywords is empty."""
        required = []
        resume = "I have experience with Python and React."
        result = identify_missing_keywords(required, resume)
        assert result == []

    def test_identify_with_punctuation_in_resume(self):
        """Test identification when keywords in resume are surrounded by punctuation."""
        required = ["Python", "React", "AWS"]
        resume = "Skills: python, react! (AWS)."
        # Assuming identify_missing_keywords uses a robust method (like extract_required_keywords)
        # for parsing the resume, which handles case-insensitivity and punctuation.
        result = identify_missing_keywords(required, resume)
        assert result == [], f"Expected no missing keywords, but got {result}"