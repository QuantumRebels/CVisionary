import re
from typing import List, Dict
from prompt_templates import render_rag_prompt

# Predefined skills list
PREDEFINED_SKILLS = [
    "Python", "AWS", "Docker", "Kubernetes", "React", "Node.js",
    "JavaScript", "TypeScript", "Java", "C++", "C#", "Go",
    "MySQL", "PostgreSQL", "MongoDB", "Redis", "Git", "Jenkins",
    "Terraform", "Ansible", "Linux", "Azure", "GCP", "Microservices",
    "REST", "GraphQL", "HTML", "CSS", "Vue.js", "Angular",
    "FastAPI", "Django", "Flask", "Spring", "Express.js", "OAuth",
    "CI/CD", "DevOps", "Agile", "Scrum", "TDD", "Machine Learning",
    "AI", "Data Science", "Pandas", "NumPy", "TensorFlow", "PyTorch"
]

def extract_keywords(text: str) -> Dict[str, List[str]]:
    """
    Extract keywords from job description text by matching against predefined skills.
    
    Args:
        text: Job description text
        
    Returns:
        Dict with 'required' and 'preferred' skill lists
    """
    found_skills = []
    
    # Convert text to lowercase for case-insensitive matching
    text_lower = text.lower()
    
    # Iterate through predefined skills
    for skill in PREDEFINED_SKILLS:
        skill_lower = skill.lower()
        escaped_skill_lower = re.escape(skill_lower)
        
        # Pattern to match the skill ensuring it's not part of a larger alphanumeric word
        # and correctly handling skills with special characters.
        # Looks for the skill either at the start (^) or preceded by a non-alphanumeric character (\W).
        # Looks for the skill either at the end ($) or followed by a non-alphanumeric character (\W).
        # The skill itself is captured. Using lookarounds to avoid consuming boundary characters.
        pattern = r'(?:^|(?<=\W))' + escaped_skill_lower + r'(?=\W|$)'
        
        if re.search(pattern, text_lower):
            found_skills.append(skill)
    
    return {
        "required": found_skills,
        "preferred": []  # Empty for now as specified
    }

def build_rag_prompt(job_description: str, chunks: List[Dict], keywords: Dict[str, List[str]]) -> str:
    """
    Build RAG prompt using chunks and keywords.
    
    Args:
        chunks: List of chunk dictionaries from embedding service
        keywords: Dict with required and preferred skills
        
    Returns:
        Formatted prompt string
    """
    # Transform chunks to minimal format needed for template
    minimal_chunks = []
    for chunk in chunks:
        minimal_chunks.append({
            "source_type": chunk.get("source_type", "unknown"),
            "source_id": chunk.get("source_id", "unknown"),
            "text": chunk.get("text", "")
        })
    
    return render_rag_prompt(job_description=job_description, chunks=minimal_chunks, keywords=keywords)