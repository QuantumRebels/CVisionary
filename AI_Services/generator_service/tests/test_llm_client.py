import pytest
import httpx
from unittest.mock import patch, AsyncMock, MagicMock
from llm_client import generate_bullets


class TestGenerateBullets:
    @pytest.fixture
    def mock_env_vars(self):
        """Fixture to mock environment variables."""
        with patch.dict('os.environ', {
            'GEMINI_API_KEY': 'test-api-key',
            'GEMINI_API_URL': 'https://api.test.com/generate'
        }):
            yield
    
    @pytest.mark.asyncio
    async def test_generate_bullets_success(self, mock_env_vars):
        """Test successful bullet generation."""
        mock_response_data = {
            "choices": [{
                "text": "- Developed Python applications\n- Deployed on AWS\n• Implemented Docker containers\n- Created REST APIs\n- Managed databases"
            }]
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_instance.post.return_value = mock_response
            
            result = await generate_bullets("Test prompt")
            
            assert len(result) == 5
            assert "Developed Python applications" in result
            assert "Deployed on AWS" in result
            assert "Implemented Docker containers" in result
            assert "Created REST APIs" in result
            assert "Managed databases" in result
            
            # Verify API call
            mock_instance.post.assert_called_once()
            call_args = mock_instance.post.call_args
            assert call_args[1]['json']['model'] == 'gemini-pro'
            assert call_args[1]['json']['prompt'] == 'Test prompt'
            assert call_args[1]['headers']['Authorization'] == 'Bearer test-api-key'
    
    @pytest.mark.asyncio
    async def test_generate_bullets_no_api_key(self):
        """Test bullet generation without API key."""
        with patch.dict('os.environ', {}, clear=True):
            result = await generate_bullets("Test prompt")
            assert result == []
    
    @pytest.mark.asyncio
    async def test_generate_bullets_api_error(self, mock_env_vars):
        """Test bullet generation with API error response."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            mock_response = MagicMock()
            mock_response.status_code = 400
            mock_instance.post.return_value = mock_response
            
            result = await generate_bullets("Test prompt")
            assert result == []
    
    @pytest.mark.asyncio
    async def test_generate_bullets_malformed_response(self, mock_env_vars):
        """Test bullet generation with malformed API response."""
        mock_response_data = {"error": "Invalid request"}
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_instance.post.return_value = mock_response
            
            result = await generate_bullets("Test prompt")
            assert result == []
    
    @pytest.mark.asyncio
    async def test_generate_bullets_empty_choices(self, mock_env_vars):
        """Test bullet generation with empty choices array."""
        mock_response_data = {"choices": []}
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_instance.post.return_value = mock_response
            
            result = await generate_bullets("Test prompt")
            assert result == []
    
    @pytest.mark.asyncio
    async def test_generate_bullets_network_error(self, mock_env_vars):
        """Test bullet generation with network error."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_instance.post.side_effect = httpx.RequestError("Network error")
            
            result = await generate_bullets("Test prompt")
            assert result == []
    
    @pytest.mark.asyncio
    async def test_generate_bullets_text_parsing(self, mock_env_vars):
        """Test bullet text parsing with various formats."""
        mock_response_data = {
            "choices": [{
                "text": "- First bullet\n• Second bullet\nThird bullet without marker\n\n   \n- Fourth bullet with spaces   \n"
            }]
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_instance.post.return_value = mock_response
            
            result = await generate_bullets("Test prompt")
            
            assert len(result) == 4
            assert "First bullet" in result
            assert "Second bullet" in result
            assert "Third bullet without marker" in result
            assert "Fourth bullet with spaces" in result
    
    @pytest.mark.asyncio
    async def test_generate_bullets_limit_bullets(self, mock_env_vars):
        """Test that bullet generation limits to 6 bullets max."""
        long_response = "\n".join([f"- Bullet {i}" for i in range(10)])
        mock_response_data = {
            "choices": [{
                "text": long_response
            }]
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_instance.post.return_value = mock_response
            
            result = await generate_bullets("Test prompt")
            
            assert len(result) == 6  # Should be limited to 6
    
    @pytest.mark.asyncio
    async def test_generate_bullets_request_parameters(self, mock_env_vars):
        """Test that correct parameters are sent to API."""
        mock_response_data = {"choices": [{"text": "- Test bullet"}]}
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_instance.post.return_value = mock_response
            
            await generate_bullets("Test prompt")
            
            call_args = mock_instance.post.call_args
            
            # Check URL
            assert call_args[0][0] == 'https://api.test.com/generate'
            
            # Check payload
            payload = call_args[1]['json']
            assert payload['model'] == 'gemini-pro'
            assert payload['prompt'] == 'Test prompt'
            assert payload['max_output_tokens'] == 256
            assert payload['temperature'] == 0.7
            
            # Check headers
            headers = call_args[1]['headers']
            assert headers['Authorization'] == 'Bearer test-api-key'
            assert headers['Content-Type'] == 'application/json'
            
            # Check timeout
            assert call_args[1]['timeout'] == 30.0