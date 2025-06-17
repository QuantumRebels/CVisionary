import re
from typing import List, Set
import logging

logger = logging.getLogger(__name__)

PREDEFINED_SKILLS = {
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust", "SQL",
    "React", "Angular", "Vue.js", "Node.js", "Django", "Flask", "FastAPI", "Spring Boot",
    "AWS", "Azure", "Google Cloud", "GCP", "Docker", "Kubernetes", "Terraform", "Git",
    "MySQL", "PostgreSQL", "MongoDB", "Redis",
    "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy",
    "REST API", "GraphQL", "Agile", "Scrum",
}

def extract_required_keywords(job_description: str) -> List[str]:
    if not job_description:
        return []
    found_skills: Set[str] = set()
    jd_lower = job_description.lower()
    for skill in PREDEFINED_SKILLS:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, jd_lower):
            found_skills.add(skill)
    return sorted(list(found_skills))

def identify_missing_keywords(required_keywords: List[str], resume_text: str) -> List[str]:
    if not required_keywords:
        return []
    if not resume_text:
        return required_keywords
    missing_skills: List[str] = []
    resume_lower = resume_text.lower()
    for skill in required_keywords:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if not re.search(pattern, resume_lower):
            missing_skills.append(skill)
    return missing_skills