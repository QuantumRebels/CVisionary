# test_app.py

import os
import pytest
import json
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
# It's good practice to import 'app' where it's reloaded, like in the client fixture
# from app import app # Can be removed if app is always obtained from reloaded module
from schemas import GenerateRequest, GenerateResponse
import importlib # <<< ADDED


class TestApp:
    @pytest.fixture
    def client(self):
        """Create test client.
        Reloads the app module to ensure it picks up patched environment variables.
        """
        from fastapi.testclient import TestClient
        import app as app_module
        importlib.reload(app_module)
        return TestClient(app_module.app)
    
    # This local mock_environment_variables can be removed if the conftest.py autouse=True
    # one is sufficient and always desired with these exact values.
    # If specific tests in TestApp need *different* env vars, keep it.
    # For now, assuming conftest.py one is primary.
    # @pytest.fixture
    # def mock_environment_variables(self):
    #     """Mock environment variables."""
    #     with patch.dict('os.environ', {
    #         'GEMINI_API_KEY': 'test-api-key',
    #         'EMBEDDING_SERVICE_URL': 'http://localhost:8001',
    #         'GEMINI_API_URL': 'https://api.gemini.google/v1/generateText'
    #     }):
    #         yield
    
    def test_missing_gemini_api_key(self, client): # client fixture reloads app
        """Test error when GEMINI_API_KEY is missing."""
        # Patch os.environ *before* the app logic (within TestClient) sees it.
        # The client fixture already reloads app, so it will see the mock_environment_variables from conftest.
        # To test missing key, we need to clear it *after* conftest's mock_environment_variables
        # has run, and then ensure the app re-reads it or TestClient is re-initialized.
        # The simplest way is to ensure the app logic inside the endpoint reads from os.getenv directly.
        # Or, for testing this specific case, create a client *inside* the patched env.
        
        import app as app_module
        original_gemini_key = os.environ.get('GEMINI_API_KEY')
        if 'GEMINI_API_KEY' in os.environ:
            del os.environ['GEMINI_API_KEY']
        
        # Reload app module so its module-level GEMINI_API_KEY is None
        importlib.reload(app_module) 
        
        # Create a new client with the reloaded app for this specific test case
        # Note: This assumes 'app' is the name of the FastAPI instance in app_module
        temp_client = TestClient(app_module.app) 

        try:
            response = temp_client.post(
                "/generate/test_user",
                json={"job_description": "Python developer role"}
            )
            assert response.status_code == 500
            assert "GEMINI_API_KEY environment variable is not set" in response.json()["detail"]
        finally:
            # Restore environment for other tests
            if original_gemini_key is not None:
                os.environ['GEMINI_API_KEY'] = original_gemini_key
            else:
                if 'GEMINI_API_KEY' in os.environ: # Should not happen if it was None
                     del os.environ['GEMINI_API_KEY']
            importlib.reload(app_module) # Reload again to restore state if needed for subsequent tests,
                                         # though pytest isolates tests. The autouse fixture will also re-apply.


    @patch('app.generate_bullets', new_callable=AsyncMock) # <<< CHANGED
    @patch('httpx.AsyncClient') # This is mock_httpx_client
    def test_successful_generation(
        self,
        mock_httpx_client, # This is the @patch('httpx.AsyncClient')
        mock_generate_bullets, # This is the @patch('app.generate_bullets')
        client, # Uses TestApp.client() which reloads app
        # mock_environment_variables, # No longer needed as argument if relying on conftest autouse
        mock_embedding_service_response,
        mock_retrieve_service_response
    ):
        """Test successful bullet generation."""
        mock_client_instance = AsyncMock()
        # mock_httpx_client is the MagicMock from @patch('httpx.AsyncClient')
        # its return_value is what httpx.AsyncClient() would return.
        mock_httpx_client.return_value.__aenter__.return_value = mock_client_instance
        
        mock_embed_response = MagicMock()
        mock_embed_response.status_code = 200
        mock_embed_response.json.return_value = mock_embedding_service_response
        
        mock_retrieve_response = MagicMock()
        mock_retrieve_response.status_code = 200
        mock_retrieve_response.json.return_value = mock_retrieve_service_response
        
        mock_client_instance.post.side_effect = [mock_embed_response, mock_retrieve_response]
        
        mock_bullets = ["Test bullet 1", "Test bullet 2"]
        mock_generate_bullets.return_value = mock_bullets # Correct for AsyncMock
        
        response = client.post(
            "/generate/test_user",
            json={"job_description": "Looking for Python developer with AWS and Docker experience"}
        )
        
        assert response.status_code == 200 # Should now pass if GEMINI_API_KEY and mock are correct
        
        mock_generate_bullets.assert_called_once()
        
        prompt = mock_generate_bullets.call_args[0][0]
        
        assert "Python" in prompt
        assert "AWS" in prompt
        assert "Docker" in prompt
        
        data = response.json()
        assert data["bullets"] == mock_bullets
        assert data["raw_prompt"] == prompt
    
    @patch('app.generate_bullets', new_callable=AsyncMock) # <<< CHANGED
    @patch('httpx.AsyncClient')
    def test_empty_chunks_handling(
        self,
        mock_httpx_client,
        mock_generate_bullets,
        client,
        # mock_environment_variables, # Not needed as arg
        mock_embedding_service_response
    ):
        """Test handling of empty chunks from retrieve service."""
        mock_client_instance = AsyncMock()
        mock_httpx_client.return_value.__aenter__.return_value = mock_client_instance
        
        mock_embed_response = MagicMock()
        mock_embed_response.status_code = 200
        mock_embed_response.json.return_value = mock_embedding_service_response
        
        mock_retrieve_response = MagicMock()
        mock_retrieve_response.status_code = 200
        mock_retrieve_response.json.return_value = {"results": []}
        
        mock_client_instance.post.side_effect = [mock_embed_response, mock_retrieve_response]
        
        mock_bullets = ["Generated bullet without user context"]
        mock_generate_bullets.return_value = mock_bullets
        
        response = client.post(
            "/generate/test_user",
            json={"job_description": "Python developer role"}
        )
        
        assert response.status_code == 200 # Expect 200
        
        mock_generate_bullets.assert_called_once()
        prompt = mock_generate_bullets.call_args[0][0]
        assert "top 0 relevant user passages" in prompt
    
    # For test_user_id_parameter, if it's not supposed to call generate_bullets,
    # then generate_bullets doesn't need to be mocked. The httpx.AsyncClient mock
    # will handle the service calls. The client fixture reloads app, so GEMINI_API_KEY is set.
    @patch('httpx.AsyncClient')
    def test_user_id_parameter(self, mock_httpx_client, client): # mock_environment_variables not needed as arg
        """Test that user_id parameter is properly handled."""
        mock_client_instance = AsyncMock()
        mock_httpx_client.return_value.__aenter__.return_value = mock_client_instance
        
        mock_embed_response = MagicMock()
        mock_embed_response.status_code = 200
        mock_embed_response.json.return_value = {"embedding": [0.1] * 384, "status": "success"}
        
        mock_retrieve_response = MagicMock()
        mock_retrieve_response.status_code = 404 # This should be caught by app.py
        # No json body needed for 404 error usually, but if app.py tries to .json() it, mock it
        mock_retrieve_response.json.return_value = {"detail": "User not found from mock"}


        mock_client_instance.post.side_effect = [mock_embed_response, mock_retrieve_response]
        
        response = client.post(
            "/generate/nonexistent_user",
            json={"job_description": "Python developer role"}
        )
        
        # The app should return 404 when the user is not found
        assert response.status_code == 404
        assert "User not found or no chunks indexed" in response.json()["detail"]
        
        retrieve_call_args = mock_client_instance.post.call_args_list[1]
        assert "/retrieve/nonexistent_user" in retrieve_call_args[0][0]
    
    @patch('app.generate_bullets', new_callable=AsyncMock) # Mock generate_bullets to prevent its actual call
    @patch('httpx.AsyncClient')
    def test_service_timeout_handling(
        self,
        mock_httpx_client,
        mock_generate_bullets, # Even if not used, good to control
        client
        # mock_environment_variables # Not needed as arg
    ):
        """Test handling of service timeouts."""
        mock_client_instance = AsyncMock()
        mock_httpx_client.return_value.__aenter__.return_value = mock_client_instance
        
        from httpx import TimeoutException
        # Ensure the mock 'post' method is async and raises the exception
        mock_client_instance.post = AsyncMock(side_effect=TimeoutException("Request timeout"))
        
        # If generate_bullets is called, ensure it returns something valid
        mock_generate_bullets.return_value = ["Fallback bullet"]


        response = client.post(
            "/generate/test_user",
            json={"job_description": "Python developer role"}
        )
        
        assert response.status_code == 502
        assert "Service communication error" in response.json()["detail"]
    
    @patch('app.generate_bullets', new_callable=AsyncMock) # <<< CHANGED
    @patch('httpx.AsyncClient')
    def test_large_job_description(
        self,
        mock_httpx_client,
        mock_generate_bullets,
        client,
        # mock_environment_variables, # Not needed as arg
        mock_embedding_service_response,
        mock_retrieve_service_response
    ):
        """Test handling of very large job descriptions."""
        mock_client_instance = AsyncMock()
        mock_httpx_client.return_value.__aenter__.return_value = mock_client_instance
        
        mock_embed_response = MagicMock()
        mock_embed_response.status_code = 200
        mock_embed_response.json.return_value = mock_embedding_service_response
        
        mock_retrieve_response = MagicMock()
        mock_retrieve_response.status_code = 200
        mock_retrieve_response.json.return_value = mock_retrieve_service_response
        
        mock_client_instance.post.side_effect = [mock_embed_response, mock_retrieve_response]
        
        mock_bullets = ["Bullet 1", "Bullet 2"]
        mock_generate_bullets.return_value = mock_bullets
        
        large_job_description = "Python developer " * 1000 + "with AWS experience"
        
        response = client.post(
            "/generate/test_user",
            json={"job_description": large_job_description}
        )
        
        assert response.status_code == 200
        
        embed_call = mock_client_instance.post.call_args_list[0]
        assert embed_call[1]['json']['text'] == large_job_description
    
    @patch('app.generate_bullets', new_callable=AsyncMock) # <<< CHANGED
    @patch('httpx.AsyncClient')
    def test_special_characters_in_job_description(
        self,
        mock_httpx_client,
        mock_generate_bullets,
        client,
        # mock_environment_variables, # Not needed as arg
        mock_embedding_service_response,
        mock_retrieve_service_response
    ):
        """Test handling of special characters in job description."""
        mock_client_instance = AsyncMock()
        mock_httpx_client.return_value.__aenter__.return_value = mock_client_instance
        
        mock_embed_response = MagicMock()
        mock_embed_response.status_code = 200
        mock_embed_response.json.return_value = mock_embedding_service_response
        
        mock_retrieve_response = MagicMock()
        mock_retrieve_response.status_code = 200
        mock_retrieve_response.json.return_value = mock_retrieve_service_response
        
        mock_client_instance.post.side_effect = [mock_embed_response, mock_retrieve_response]
        
        mock_bullets = ["Bullet 1", "Bullet 2"]
        mock_generate_bullets.return_value = mock_bullets
        
        special_job_description = 'Looking for "Python" developer with 50% remote work & $100K+ salary'
        
        response = client.post(
            "/generate/test_user",
            json={"job_description": special_job_description}
        )
        
        assert response.status_code == 200
        
        embed_call = mock_client_instance.post.call_args_list[0]
        assert embed_call[1]['json']['text'] == special_job_description


class TestAppStartup:
    """Test application startup and configuration."""
    
    def test_app_title(self, test_client): # Use test_client which reloads app
        """Test that the app has the correct title."""
        # Accessing app directly from module might use non-reloaded version
        # It's better to get app properties via the client or by reloading it here too
        import app as app_module
        importlib.reload(app_module)
        assert app_module.app.title == "CVisionary Generator Service"
    
    def test_app_routes(self, test_client): # Use test_client which reloads app
        """Test that the expected routes exist."""
        import app as app_module
        importlib.reload(app_module)
        routes = [route.path for route in app_module.app.routes]
        assert "/generate/{user_id}" in routes
    
    @patch.dict('os.environ', {
        'EMBEDDING_SERVICE_URL': 'http://custom:9999',
        'GEMINI_API_KEY': 'custom-key',
        'GEMINI_API_URL': 'https://custom.api.com'
    })
    def test_environment_variable_loading(self): # test_client not strictly needed if only checking module vars
        """Test that environment variables are loaded correctly."""
        import importlib
        import app as app_module
        importlib.reload(app_module) # Crucial: reload after os.environ is patched
        
        assert app_module.EMBEDDING_SERVICE_URL == 'http://custom:9999'
        # GEMINI_API_KEY is read at module level in app.py
        # So after reload, it should pick up the 'custom-key'
        assert app_module.GEMINI_API_KEY == 'custom-key' 
        assert app_module.GEMINI_API_URL == 'https://custom.api.com'
        
    @patch('app.generate_bullets', new_callable=AsyncMock) # Mock to prevent real call
    @patch('httpx.AsyncClient')
    def test_embedding_service_failure(self, mock_httpx_client, mock_generate_bullets, test_client): # mock_environment_variables not needed as arg
        """Test embedding service failure."""
        mock_client_instance = AsyncMock()
        mock_httpx_client.return_value.__aenter__.return_value = mock_client_instance
        
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"detail": "embed error from mock"} # If app tries to .json()
        mock_client_instance.post.return_value = mock_response # Only one call, to embed
        
        mock_generate_bullets.return_value = ["Fallback"]


        response = test_client.post(
            "/generate/test_user",
            json={"job_description": "Python developer role"}
        )
        
        assert response.status_code == 502
        assert "Embedding service failure" in response.json()["detail"]
    
    @patch('app.generate_bullets', new_callable=AsyncMock) # Mock to prevent real call
    @patch('httpx.AsyncClient')
    def test_embedding_service_malformed_response(self, mock_httpx_client, mock_generate_bullets, test_client): # mock_environment_variables not needed
        """Test embedding service malformed response."""
        mock_client_instance = AsyncMock()
        mock_httpx_client.return_value.__aenter__.return_value = mock_client_instance
        
        mock_response = MagicMock()
        mock_response.status_code = 200 # Service returns 200 but bad content
        mock_response.json.return_value = {"error": "Something went wrong", "embedding": None} # Malformed
        mock_client_instance.post.return_value = mock_response

        mock_generate_bullets.return_value = ["Fallback"]

        response = test_client.post(
            "/generate/test_user",
            json={"job_description": "Python developer role"}
        )
        
        assert response.status_code == 502
        assert "Embedding service failure" in response.json()["detail"] # As app.py checks "embedding" key
    
    @patch('app.generate_bullets', new_callable=AsyncMock) # Mock to prevent real call
    @patch('httpx.AsyncClient')
    def test_retrieve_service_failure(
        self,
        mock_httpx_client,
        mock_generate_bullets,
        test_client,
        # mock_environment_variables, # Not needed
        mock_embedding_service_response # This is for the *successful* embed call
    ):
        """Test retrieve service failure."""
        mock_client_instance = AsyncMock()
        mock_httpx_client.return_value.__aenter__.return_value = mock_client_instance
        
        mock_embed_response = MagicMock()
        mock_embed_response.status_code = 200
        mock_embed_response.json.return_value = mock_embedding_service_response # Successful embed
        
        mock_retrieve_response = MagicMock()
        mock_retrieve_response.status_code = 404 # Failed retrieve
        mock_retrieve_response.json.return_value = {"detail":"not found mock"}

        mock_client_instance.post.side_effect = [mock_embed_response, mock_retrieve_response]
        mock_generate_bullets.return_value = ["Fallback"]

        response = test_client.post(
            "/generate/test_user",
            json={"job_description": "Python developer role"}
        )
        
        assert response.status_code == 404
        assert "User not found or no chunks indexed" in response.json()["detail"]
    
    @patch('app.generate_bullets', new_callable=AsyncMock) # <<< Key change here
    @patch('httpx.AsyncClient')
    def test_llm_generation_failure(
        self,
        mock_httpx_client,
        mock_generate_bullets, # This is the one we control for failure
        test_client,
        # mock_environment_variables, # Not needed
        mock_embedding_service_response,
        mock_retrieve_service_response
    ):
        """Test LLM generation failure."""
        mock_client_instance = AsyncMock()
        mock_httpx_client.return_value.__aenter__.return_value = mock_client_instance
        
        mock_embed_response = MagicMock()
        mock_embed_response.status_code = 200
        mock_embed_response.json.return_value = mock_embedding_service_response
        
        mock_retrieve_response = MagicMock()
        mock_retrieve_response.status_code = 200
        mock_retrieve_response.json.return_value = mock_retrieve_service_response
        
        mock_client_instance.post.side_effect = [mock_embed_response, mock_retrieve_response]
        
        mock_generate_bullets.return_value = [] # Simulate LLM returning no bullets
        
        response = test_client.post(
            "/generate/test_user",
            json={"job_description": "Python developer role"}
        )
        
        assert response.status_code == 502
        assert "Failed to generate bullet points from LLM" in response.json()["detail"]
    
    @patch('app.generate_bullets', new_callable=AsyncMock) # Mock to prevent real call
    @patch('httpx.AsyncClient')
    def test_network_error(self, mock_httpx_client, mock_generate_bullets, test_client): # mock_environment_variables not needed
        """Test network error handling."""
        mock_client_instance = AsyncMock()
        mock_httpx_client.return_value.__aenter__.return_value = mock_client_instance
        
        from httpx import RequestError
        # mock_client_instance.post.side_effect = RequestError("Network error")
        mock_client_instance.post = AsyncMock(side_effect=RequestError("Network error"))


        mock_generate_bullets.return_value = ["Fallback"]

        response = test_client.post(
            "/generate/test_user",
            json={"job_description": "Python developer role"}
        )
        
        assert response.status_code == 502
        assert "Service communication error" in response.json()["detail"]
    
    def test_invalid_request_body(self, test_client): # mock_environment_variables not needed
        """Test invalid request body."""
        response = test_client.post(
            "/generate/test_user",
            json={"invalid_field": "value"} # FastAPI should give 422
        )
        assert response.status_code == 422
    
    def test_empty_request_body(self, test_client): # mock_environment_variables not needed
        """Test empty request body."""
        response = test_client.post(
            "/generate/test_user",
            json={} # FastAPI should give 422 as job_description is required
        )
        assert response.status_code == 422
    
    @patch('app.generate_bullets', new_callable=AsyncMock) # <<< CHANGED
    @patch('httpx.AsyncClient')
    def test_keyword_extraction_integration(
        self,
        mock_httpx_client,
        mock_generate_bullets,
        test_client, # Uses reloaded app
        # mock_environment_variables, # Not needed
        mock_embedding_service_response,
        mock_retrieve_service_response
    ):
        """Test that keywords are properly extracted and included in prompt."""
        mock_client_instance = AsyncMock()
        mock_httpx_client.return_value.__aenter__.return_value = mock_client_instance
        
        mock_embed_response = MagicMock()
        mock_embed_response.status_code = 200
        mock_embed_response.json.return_value = mock_embedding_service_response
        
        mock_retrieve_response = MagicMock()
        mock_retrieve_response.status_code = 200
        mock_retrieve_response.json.return_value = mock_retrieve_service_response
        
        mock_client_instance.post.side_effect = [mock_embed_response, mock_retrieve_response]
        
        mock_generate_bullets.return_value = ["Bullet 1", "Bullet 2"]
        
        job_desc_text = "Python developer role"
        response = test_client.post(
            "/generate/test_user",
            json={"job_description": job_desc_text}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["bullets"]) == 2
        assert "Bullet 1" in data["bullets"]
        assert "raw_prompt" in data
        
        # Check that the job description and extracted keywords are in the prompt
        mock_generate_bullets.assert_called_once()
        prompt_arg = mock_generate_bullets.call_args[0][0]
        assert job_desc_text in prompt_arg
        assert "Python" in prompt_arg # Assuming extract_keywords finds "Python"