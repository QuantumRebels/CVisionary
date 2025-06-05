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
    
    # Iterate through predefined skills and match with word boundaries
    for skill in PREDEFINED_SKILLS:
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.append(skill)
    
    return {
        "required": found_skills,
        "preferred": []  # Empty for now as specified
    }

def build_rag_prompt(chunks: List[Dict], keywords: Dict[str, List[str]]) -> str:
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
    
    return render_rag_prompt(minimal_chunks, keywords)