"""Tests for GitHub MCP Server."""

import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.config import Config
from server.github_api import GitHubAPI, GitHubAPIError, RateLimitError


class TestConfig:
    """Test configuration management."""
    
    def test_config_from_env(self):
        """Test loading configuration from environment."""
        with patch.dict(os.environ, {
            "GITHUB_TOKEN": "test_token",
            "GITHUB_API_TIMEOUT": "60"
        }):
            config = Config.from_env()
            assert config.github_token == "test_token"
            assert config.timeout == 60
    
    def test_config_validation_missing_token(self):
        """Test that validation fails without token."""
        config = Config(github_token=None)
        with pytest.raises(ValueError, match="GITHUB_TOKEN"):
            config.validate()
    
    def test_config_validation_with_token(self):
        """Test that validation passes with token."""
        config = Config(github_token="test_token")
        config.validate()  # Should not raise


class TestGitHubAPI:
    """Test GitHub API wrapper."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return Config(github_token="test_token")
    
    @pytest.fixture
    def github_api(self, config):
        """Create GitHub API instance."""
        return GitHubAPI(config)
    
    def test_session_creation(self, github_api):
        """Test that session is created with correct headers."""
        assert "Authorization" in github_api.session.headers
        assert github_api.session.headers["Authorization"] == "Bearer test_token"
        assert "Accept" in github_api.session.headers
    
    @patch('server.github_api.requests.Session.request')
    def test_search_repositories_success(self, mock_request, github_api):
        """Test successful repository search."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            "X-RateLimit-Remaining": "5000",
            "X-RateLimit-Reset": "1234567890"
        }
        mock_response.json.return_value = {
            "items": [
                {
                    "full_name": "test/repo",
                    "description": "Test repo",
                    "stargazers_count": 100,
                    "forks_count": 50,
                    "language": "Python",
                    "html_url": "https://github.com/test/repo",
                    "topics": ["test"],
                    "open_issues_count": 5
                }
            ]
        }
        mock_request.return_value = mock_response
        
        results = github_api.search_repositories("test")
        assert len(results) == 1
        assert results[0]["name"] == "test/repo"
        assert results[0]["stars"] == 100
    
    @patch('server.github_api.requests.Session.request')
    def test_search_repositories_empty(self, mock_request, github_api):
        """Test repository search with no results."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            "X-RateLimit-Remaining": "5000",
            "X-RateLimit-Reset": "1234567890"
        }
        mock_response.json.return_value = {"items": []}
        mock_request.return_value = mock_response
        
        results = github_api.search_repositories("nonexistent")
        assert results == []
    
    @patch('server.github_api.requests.Session.request')
    def test_rate_limit_error(self, mock_request, github_api):
        """Test rate limit handling."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.text = "API rate limit exceeded"
        mock_response.headers = {
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": "1234567890"
        }
        mock_request.return_value = mock_response
        
        with pytest.raises(RateLimitError):
            github_api.search_repositories("test")
    
    @patch('server.github_api.requests.Session.request')
    def test_not_found_error(self, mock_request, github_api):
        """Test 404 error handling."""
        from requests.exceptions import HTTPError
        
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_response.headers = {
            "X-RateLimit-Remaining": "5000",
            "X-RateLimit-Reset": "1234567890"
        }
        
        # Create HTTPError with the response
        http_error = HTTPError("404 Error")
        http_error.response = mock_response
        mock_response.raise_for_status.side_effect = http_error
        mock_request.return_value = mock_response
        
        with pytest.raises(GitHubAPIError, match="Resource not found"):
            github_api.get_repository("nonexistent", "repo")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
