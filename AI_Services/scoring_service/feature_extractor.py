import re
from typing import List
import logging

logger = logging.getLogger(__name__)

# Predefined skill list for keyword extraction
PREDEFINED_SKILLS = [
    # Programming Languages
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust", "PHP", "Ruby",
    "Swift", "Kotlin", "Scala", "R", "MATLAB", "SQL", "HTML", "CSS",
    
    # Frameworks and Libraries
    "React", "Angular", "Vue.js", "Node.js", "Express.js", "Django", "Flask", "FastAPI",
    "Spring Boot", "ASP.NET", "Laravel", "Ruby on Rails", "Next.js", "Nuxt.js",
    
    # Cloud Platforms
    "AWS", "Azure", "Google Cloud", "GCP", "Heroku", "DigitalOcean", "Vercel", "Netlify",
    
    # DevOps and Tools
    "Docker", "Kubernetes", "Jenkins", "GitLab CI/CD", "GitHub Actions", "Terraform",
    "Ansible", "Chef", "Puppet", "Vagrant", "Helm",
    
    # Databases
    "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch", "Cassandra", "DynamoDB",
    "SQLite", "Oracle", "SQL Server",
    
    # Data Science and ML
    "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy", "Matplotlib", "Seaborn",
    "Jupyter", "Apache Spark", "Hadoop", "Kafka", "Airflow",
    
    # Mobile Development
    "React Native", "Flutter", "Xamarin", "Ionic", "Android", "iOS",
    
    # Testing
    "Jest", "Mocha", "Chai", "Cypress", "Selenium", "PyTest", "JUnit", "TestNG",
    
    # Version Control
    "Git", "SVN", "Mercurial",
    
    # Operating Systems
    "Linux", "Ubuntu", "CentOS", "RHEL", "Windows", "macOS",
    
    # Web Technologies
    "REST API", "GraphQL", "gRPC", "WebSockets", "OAuth", "JWT", "SOAP",
    
    # Monitoring and Analytics
    "Prometheus", "Grafana", "New Relic", "Datadog", "Splunk", "ELK Stack",
    
    # Project Management
    "Agile", "Scrum", "Kanban", "Jira", "Confluence", "Slack", "Trello",
    
    # Design Tools
    "Figma", "Adobe XD", "Sketch", "Photoshop", "Illustrator"
]

def extract_required_keywords(job_description: str) -> List[str]:
    """
    Extract required skills/keywords from job description
    
    Args:
        job_description: Job description text
        
    Returns:
        List of required skills found in the job description
    """
    if not job_description:
        return []
    
    try:
        # Convert job description to lowercase for case-insensitive matching
        jd_lower = job_description.lower()
        
        # Find matching skills
        found_skills = []
        for skill in PREDEFINED_SKILLS:
            skill_lower = skill.lower()
            
            # Use word boundaries to avoid partial matches
            # Handle skills with special characters (like C++, C#)
            if skill_lower in ["c++", "c#"]:
                if skill_lower in jd_lower:
                    found_skills.append(skill)
            else:
                # Use regex with word boundaries for better matching
                pattern = r'\b' + re.escape(skill_lower) + r'\b'
                if re.search(pattern, jd_lower):
                    found_skills.append(skill)
        
        logger.info(f"Extracted {len(found_skills)} required keywords from job description")
        return found_skills
        
    except Exception as e:
        logger.error(f"Error extracting keywords: {str(e)}")
        return []

def identify_missing_keywords(required_keywords: List[str], resume_text: str) -> List[str]:
    """
    Identify which required keywords are missing from the resume
    
    Args:
        required_keywords: List of required skills
        resume_text: Resume text content
        
    Returns:
        List of missing skills not found in the resume
    """
    if not required_keywords or not resume_text:
        return required_keywords if required_keywords else []
    
    try:
        # Convert resume text to lowercase for case-insensitive matching
        resume_lower = resume_text.lower()
        
        missing_skills = []
        for skill in required_keywords:
            skill_lower = skill.lower()
            
            # Handle special cases for programming languages
            if skill_lower in ["c++", "c#"]:
                if skill_lower not in resume_lower:
                    missing_skills.append(skill)
            else:
                # Use regex with word boundaries for better matching
                pattern = r'\b' + re.escape(skill_lower) + r'\b'
                if not re.search(pattern, resume_lower):
                    missing_skills.append(skill)
        
        logger.info(f"Identified {len(missing_skills)} missing keywords")
        return missing_skills
        
    except Exception as e:
        logger.error(f"Error identifying missing keywords: {str(e)}")
        return required_keywords