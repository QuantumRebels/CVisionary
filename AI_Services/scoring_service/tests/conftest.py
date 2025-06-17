import pytest

@pytest.fixture(scope="function", autouse=True)
def set_test_environment(monkeypatch):
    """
    Automatically sets required environment variables for every test function.
    Using function scope to match the scope of the 'monkeypatch' fixture.
    """
    monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")