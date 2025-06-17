from scoring_service.feature_extractor import extract_required_keywords, identify_missing_keywords

def test_extract_required_keywords():
    jd = "We need a Python developer with FastAPI experience. Knowledge of AWS and Docker is a plus."
    expected = ["AWS", "Docker", "FastAPI", "Python"]
    assert extract_required_keywords(jd) == expected

def test_identify_missing_keywords():
    required = ["AWS", "Docker", "FastAPI", "Python"]
    resume = "I am a Python developer who loves the FastAPI framework."
    expected_missing = ["AWS", "Docker"]
    assert identify_missing_keywords(required, resume) == expected_missing

def test_keyword_logic_with_no_matches():
    assert extract_required_keywords("A job for a baker.") == []
    assert identify_missing_keywords(["Python"], "I am a Python developer.") == []