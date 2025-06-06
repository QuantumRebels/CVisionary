import pytest
import os
import logging
from unittest.mock import patch, AsyncMock, MagicMock
import httpx
from ..suggestion_client import SuggestionClient, logger as suggestion_logger # Adjusted import


@pytest.fixture
def client_no_env_vars(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_URL", raising=False)
    return SuggestionClient()

@pytest.fixture
def client_with_api_key(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test_api_key")
    monkeypatch.delenv("GEMINI_API_URL", raising=False)
    return SuggestionClient()

@pytest.fixture
def client_with_all_vars(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test_api_key")
    monkeypatch.setenv("GEMINI_API_URL", "https://custom.gemini.url/api")
    return SuggestionClient()

class TestSuggestionClientInit:
    def test_init_no_api_key(self, client_no_env_vars, caplog):
        with caplog.at_level(logging.WARNING):
            # Re-initialize the client to capture the log message
            client = SuggestionClient()
            
            assert client.api_key is None
            assert client.api_url == "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
            
            # Check that the warning was logged
            assert len(caplog.records) > 0, "No log records captured"
            assert any(
                record.levelname == "WARNING" and 
                "GEMINI_API_KEY not found in environment variables" in record.message and
                record.name == "scoring_service.suggestion_client"
                for record in caplog.records
            ), f"Expected log message not found in records: {caplog.records}"

    def test_init_with_api_key(self, client_with_api_key):
        assert client_with_api_key.api_key == "test_api_key"
        assert client_with_api_key.api_url == "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

    def test_init_with_custom_url(self, client_with_all_vars):
        assert client_with_all_vars.api_key == "test_api_key"
        assert client_with_all_vars.api_url == "https://custom.gemini.url/api"

class TestSuggestionClientBuildPrompt:
    def test_build_prompt_basic(self, client_no_env_vars):
        skills = "Python, Docker"
        prompt = client_no_env_vars._build_prompt(skills)
        assert "missing these skills for a job: Python, Docker" in prompt
        assert "exactly 3 concise, actionable bullet-point suggestions" in prompt
        assert "• [Suggestion 1]" in prompt
        assert "• [Suggestion 2]" in prompt
        assert "• [Suggestion 3]" in prompt
        assert "Keep each suggestion under 20 words" in prompt

class TestSuggestionClientParseSuggestions:
    @pytest.mark.parametrize("response_text, expected_suggestions", [
        (
            "• Suggestion 1: Learn Python basics.\n• Suggestion 2: Take a Docker course.\n• Suggestion 3: Build a project.",
            ["Suggestion 1: Learn Python basics.", "Suggestion 2: Take a Docker course.", "Suggestion 3: Build a project."]
        ),
        (
            "- Item A\n- Item B",
            ["Item A", "Item B"]
        ),
        (
            "* Point one\n* Point two is a bit longer but still okay.",
            ["Point one", "Point two is a bit longer but still okay."]
        ),
        (
            "1. First suggestion.\n2. Second suggestion, quite good.\n3. Third one.",
            ["First suggestion.", "Second suggestion, quite good.", "Third one."]
        ),
        (
            "This is a sentence. This is another sentence. And a third one.",
            ["This is a sentence", "This is another sentence", "And a third one"] # Assuming split by '.'
        ),
        (
            "• Valid suggestion one.\n• This suggestion is way too long and should definitely be ignored by the parser because it exceeds the twenty-five word limit established for this particular test case.",
            ["Valid suggestion one."]
        ),
        (
            "No bullets here, just plain text. Maybe another sentence.",
            ["No bullets here, just plain text", "Maybe another sentence"] # Assuming split by '.'
        ),
        (
            "", # Empty response
            []
        ),
        (
            "Just one suggestion that is short.",
            ["Just one suggestion that is short"]
        ),
         (
            "• Suggestion 1\n•\n• Suggestion 3", # Empty bullet
            ["Suggestion 1", "Suggestion 3"]
        )
    ])
    def test_parse_suggestions(self, client_no_env_vars, response_text, expected_suggestions):
        suggestions = client_no_env_vars._parse_suggestions(response_text)
        assert suggestions == expected_suggestions

    def test_parse_suggestions_error_handling(self, client_no_env_vars, caplog):
        # Test that an error during parsing (e.g., if re.split fails unexpectedly) is caught
        with patch('re.split', side_effect=Exception("Regex boom!")):
            suggestions = client_no_env_vars._parse_suggestions("Some text.")
            assert suggestions == []
            assert "Error parsing suggestions: Regex boom!" in caplog.text


@pytest.mark.asyncio
class TestSuggestionClientCallGeminiAPI:
    @patch('httpx.AsyncClient.post')
    async def test_call_gemini_api_success(self, mock_post, client_with_api_key):
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json = MagicMock(return_value={
            "candidates": [{
                "content": {
                    "parts": [{"text": "Generated text"}]
                }
            }]
        })
        mock_post.return_value = mock_response

        result = await client_with_api_key._call_gemini_api("Test prompt")
        assert result == "Generated text"
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == f"{client_with_api_key.api_url}?key={client_with_api_key.api_key}"
        assert call_args[1]['json']['contents'][0]['parts'][0]['text'] == "Test prompt"

    @patch('httpx.AsyncClient.post')
    async def test_call_gemini_api_http_error(self, mock_post, client_with_api_key, caplog):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.side_effect = httpx.HTTPStatusError("Error", request=MagicMock(), response=mock_response)

        with pytest.raises(httpx.HTTPStatusError):
            await client_with_api_key._call_gemini_api("Test prompt")
        assert "HTTP error calling Gemini API: 400 - Bad Request" in caplog.text

    @patch('httpx.AsyncClient.post')
    async def test_call_gemini_api_network_error(self, mock_post, client_with_api_key, caplog):
        mock_post.side_effect = httpx.RequestError("Network issue", request=MagicMock())

        with pytest.raises(httpx.RequestError):
            await client_with_api_key._call_gemini_api("Test prompt")
        assert "Error calling Gemini API: Network issue" in caplog.text
    
    @patch('httpx.AsyncClient.post')
    async def test_call_gemini_api_no_candidates(self, mock_post, client_with_api_key, caplog):
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json = MagicMock(return_value={"candidates": []}) # No candidates
        mock_post.return_value = mock_response

        result = await client_with_api_key._call_gemini_api("Test prompt")
        assert result == ""
        assert "No valid response from Gemini API" in caplog.text

    @patch('httpx.AsyncClient.post')
    async def test_call_gemini_api_no_content_parts(self, mock_post, client_with_api_key, caplog):
        # Create individual mock responses for each call in the loop
        mock_response1 = MagicMock(spec=httpx.Response)
        mock_response1.status_code = 200
        mock_response1.raise_for_status = MagicMock()
        mock_response1.json = MagicMock(return_value={"candidates": [{"content": {"parts": []}}]}) # No parts

        mock_response2 = MagicMock(spec=httpx.Response)
        mock_response2.status_code = 200
        mock_response2.raise_for_status = MagicMock()
        mock_response2.json = MagicMock(return_value={"candidates": [{"content": {}}]}) # No content key

        mock_response3 = MagicMock(spec=httpx.Response)
        mock_response3.status_code = 200
        mock_response3.raise_for_status = MagicMock()
        mock_response3.json = MagicMock(return_value={"candidates": [{}]}) # No content in candidate

        mock_post.side_effect = [mock_response1, mock_response2, mock_response3]
        
        for i in range(3):
            result = await client_with_api_key._call_gemini_api("Test prompt")
            assert result == ""
            assert "No valid response from Gemini API" in caplog.text
        assert mock_post.call_count == 3


@pytest.mark.asyncio
class TestSuggestionClientGenerateSuggestions:
    async def test_generate_suggestions_no_api_key(self, client_no_env_vars, caplog):
        suggestions = await client_no_env_vars.generate_suggestions(["Python"])
        assert suggestions == []
        assert "Cannot generate suggestions: GEMINI_API_KEY not configured" in caplog.text

    async def test_generate_suggestions_no_missing_skills(self, client_with_api_key):
        suggestions = await client_with_api_key.generate_suggestions([])
        assert suggestions == []

    @patch.object(SuggestionClient, '_build_prompt', return_value="Test Prompt")
    @patch.object(SuggestionClient, '_call_gemini_api', new_callable=AsyncMock, return_value="• Sug 1\n• Sug 2\n• Sug 3\n• Sug 4")
    @patch.object(SuggestionClient, '_parse_suggestions', return_value=["Sug 1", "Sug 2", "Sug 3", "Sug 4"])
    async def test_generate_suggestions_success(self, mock_parse, mock_call_api, mock_build_prompt, client_with_api_key):
        missing_skills = ["Python", "Java", "Docker", "Kubernetes", "AWS", "GCP"]
        suggestions = await client_with_api_key.generate_suggestions(missing_skills)
        
        assert suggestions == ["Sug 1", "Sug 2", "Sug 3"] # Returns max 3
        mock_build_prompt.assert_called_once_with("Python, Java, Docker, Kubernetes, AWS") # Max 5 skills to prompt
        mock_call_api.assert_called_once_with("Test Prompt")
        mock_parse.assert_called_once_with("• Sug 1\n• Sug 2\n• Sug 3\n• Sug 4")

    @patch.object(SuggestionClient, '_call_gemini_api', new_callable=AsyncMock, side_effect=Exception("API Call Failed"))
    async def test_generate_suggestions_api_call_fails(self, mock_call_api, client_with_api_key, caplog):
        suggestions = await client_with_api_key.generate_suggestions(["Python"])
        assert suggestions == []
        assert "Failed to generate suggestions: API Call Failed" in caplog.text

    @patch.object(SuggestionClient, '_call_gemini_api', new_callable=AsyncMock, return_value="Raw API Response")
    @patch.object(SuggestionClient, '_parse_suggestions', side_effect=Exception("Parsing Failed"))
    async def test_generate_suggestions_parsing_fails(self, mock_parse, mock_call_api, client_with_api_key, caplog):
        suggestions = await client_with_api_key.generate_suggestions(["Python"])
        assert suggestions == []
        assert "Failed to generate suggestions: Parsing Failed" in caplog.text
