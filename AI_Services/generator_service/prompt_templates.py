from jinja2 import Template

RAG_PROMPT_TEMPLATE = """
Based on the job description: "{{ job_description }}"

The job requires: {{ required_skills | join(", ") }}.
Preferred skills: {{ preferred_skills | join(", ") }}.

Here are the top {{ chunks | length }} relevant user passages:
{% for chunk in chunks %}
- {{ chunk.source_type }} (ID: {{ chunk.source_id }}): "{{ chunk.text }}"
{% endfor %}

Generate 5 concise bullet points (maximum 20 words each) that align the user's experience with the job requirements.
"""

def render_rag_prompt(job_description: str, chunks: list[dict], keywords: dict) -> str:
    template = Template(RAG_PROMPT_TEMPLATE)
    return template.render(
        job_description=job_description,
        required_skills=keywords["required"],
        preferred_skills=keywords["preferred"],
        chunks=chunks
    )