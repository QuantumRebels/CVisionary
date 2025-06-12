import nltk
from typing import List, Tuple

# Download NLTK punkt tokenizer data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

def chunk_text(text: str, max_words: int = 150) -> List[str]:
    """
    Split text into chunks of approximately max_words words each.
    Uses sentence boundaries to avoid cutting sentences in half.
    """
    if not text or not text.strip():
        return []
    
    sentences = nltk.sent_tokenize(text)
    
    chunks = []
    current_chunk = []
    current_word_count = 0
    
    for sentence in sentences:
        sentence_words = len(sentence.split())
        
        if current_word_count + sentence_words > max_words and current_chunk:
            chunks.append(' '.join(current_chunk))
            current_chunk = [sentence]
            current_word_count = sentence_words
        else:
            current_chunk.append(sentence)
            current_word_count += sentence_words
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def extract_text_fields(profile_data: dict) -> List[Tuple[str, str, str]]:
    """
    Extract text fields from profile JSON and return list of (source_type, source_id, text) tuples.
    """
    text_fields = []
    
    if 'experience' in profile_data:
        for i, exp in enumerate(profile_data['experience']):
            if 'description' in exp and exp['description']:
                text_fields.append(('experience', str(i), exp['description']))
    
    if 'projects' in profile_data:
        for i, project in enumerate(profile_data['projects']):
            if 'description' in project and project['description']:
                text_fields.append(('project', str(i), project['description']))
    
    if 'skills' in profile_data and profile_data['skills']:
        skills_text = ', '.join(str(skill) for skill in profile_data['skills']) if isinstance(profile_data['skills'], list) else str(profile_data['skills'])
        if skills_text:
            text_fields.append(('skills', '0', skills_text))
            
    for key in ['summary', 'bio']:
        if key in profile_data and profile_data[key]:
            text_fields.append((key, '0', profile_data[key]))
            
    return text_fields