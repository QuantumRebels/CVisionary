# feature_extractor.py

import re
from typing import List, Set
import logging

logger = logging.getLogger(__name__)

# A predefined set of skills for faster lookups.
PREDEFINED_SKILLS = {
    # Programming Languages
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust", "PHP", "Ruby",
    "Swift", "Kotlin", "Scala", "R", "SQL", "HTML", "CSS",
    # Frameworks and Libraries
    "React", "Angular", "Vue.js", "Node.js", "Express.js", "Django", "Flask", "FastAPI",
    "Spring Boot", ".NET", "Ruby on Rails", "Next.js",
    # Cloud & DevOps
    "AWS", "Azure", "Google Cloud", "GCP", "Docker", "Kubernetes", "Terraform", "Jenkins",
    "Git", "CI/CD",
    # Databases
    "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch", "DynamoDB",
    # Data Science & ML
    "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy", "Apache Spark", "Kafka",
    # Other
    "REST API", "GraphQL", "Agile", "Scrum",
}

def extract_required_keywords(job_description: str) -> List[str]:
    """Extracts important skills and technologies from a job description."""
    if not job_description:
        return []

    found_skills: Set[str] = set()
    jd_lower = job_description.lower()

    for skill in PREDEFINED_SKILLS:
        # Create a regex pattern that looks for the skill as a whole word, case-insensitive.
        # This handles single words, multi-word phrases, and skills with special characters.
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, jd_lower):
            found_skills.add(skill)
            
    logger.info(f"Extracted {len(found_skills)} keywords: {list(found_skills)}")
    return sorted(list(found_skills))

def identify_missing_keywords(required_keywords: List[str], resume_text: str) -> List[str]:
    """Compares the list of required keywords against the resume text."""
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
            
    logger.info(f"Identified {len(missing_skills)} missing keywords.")
    return missing_skills