"""
GitHub API wrapper with error handling and rate limiting.
"""

import logging
import time
from typing import Any, Dict, List, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import Config

logger = logging.getLogger(__name__)


class GitHubAPIError(Exception):
    """Custom exception for GitHub API errors."""
    pass


class RateLimitError(GitHubAPIError):
    """Raised when GitHub API rate limit is exceeded."""
    pass


class GitHubAPI:
    """Wrapper for GitHub API with error handling and resilience."""
    
    def __init__(self, config: Config):
        self.config = config
        self.session = self._create_session()
        self._rate_limit_remaining = None
        self._rate_limit_reset = None
    
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "PATCH", "DELETE"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        
        # Set default headers
        session.headers.update({
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        })
        
        if self.config.github_token:
            session.headers.update({
                "Authorization": f"Bearer {self.config.github_token}"
            })
        
        return session
    
    def _check_rate_limit(self, response: requests.Response) -> None:
        """Check and log rate limit information."""
        self._rate_limit_remaining = int(response.headers.get("X-RateLimit-Remaining", 0))
        self._rate_limit_reset = int(response.headers.get("X-RateLimit-Reset", 0))
        
        if self._rate_limit_remaining < 10:
            reset_time = time.strftime('%Y-%m-%d %H:%M:%S', 
                                       time.localtime(self._rate_limit_reset))
            logger.warning(
                f"Rate limit low: {self._rate_limit_remaining} remaining. "
                f"Resets at {reset_time}"
            )
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """Make a request to GitHub API with error handling."""
        url = f"{self.config.github_api_base_url}{endpoint}"
        
        try:
            logger.info(f"Making {method} request to {endpoint}")
            response = self.session.request(
                method, 
                url, 
                timeout=self.config.timeout,
                **kwargs
            )
            
            # Check rate limit
            self._check_rate_limit(response)
            
            # Handle rate limit exceeded
            if response.status_code == 403 and "rate limit exceeded" in response.text.lower():
                reset_time = time.strftime('%Y-%m-%d %H:%M:%S', 
                                           time.localtime(self._rate_limit_reset))
                raise RateLimitError(
                    f"GitHub API rate limit exceeded. Resets at {reset_time}"
                )
            
            # Raise for other HTTP errors
            response.raise_for_status()
            
            return response.json() if response.content else {}
            
        except requests.exceptions.Timeout:
            logger.error(f"Request to {endpoint} timed out")
            raise GitHubAPIError(f"Request timed out after {self.config.timeout} seconds")
        
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            raise GitHubAPIError("Failed to connect to GitHub API")
        
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            if e.response.status_code == 404:
                raise GitHubAPIError("Resource not found")
            elif e.response.status_code == 401:
                raise GitHubAPIError("Authentication failed. Check your GitHub token")
            else:
                raise GitHubAPIError(f"HTTP {e.response.status_code}: {e.response.text}")
    
    def search_repositories(
        self, 
        query: str, 
        sort: str = "stars", 
        order: str = "desc",
        per_page: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for GitHub repositories.
        
        Args:
            query: Search query (e.g., "language:python stars:>1000")
            sort: Sort field (stars, forks, help-wanted-issues, updated)
            order: Sort order (asc, desc)
            per_page: Number of results per page (max 100)
        
        Returns:
            List of repository information dictionaries
        """
        params = {
            "q": query,
            "sort": sort,
            "order": order,
            "per_page": min(per_page, 100)
        }
        
        result = self._make_request("GET", "/search/repositories", params=params)
        
        if not result.get("items"):
            logger.info(f"No repositories found for query: {query}")
            return []
        
        # Extract relevant information
        repositories = []
        for item in result["items"]:
            repositories.append({
                "name": item["full_name"],
                "description": item.get("description", "No description"),
                "stars": item["stargazers_count"],
                "forks": item["forks_count"],
                "language": item.get("language", "Unknown"),
                "url": item["html_url"],
                "topics": item.get("topics", []),
                "open_issues": item.get("open_issues_count", 0)
            })
        
        logger.info(f"Found {len(repositories)} repositories")
        return repositories
    
    def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific repository.
        
        Args:
            owner: Repository owner username
            repo: Repository name
        
        Returns:
            Repository information dictionary
        """
        result = self._make_request("GET", f"/repos/{owner}/{repo}")
        
        return {
            "name": result["full_name"],
            "description": result.get("description", "No description"),
            "stars": result["stargazers_count"],
            "forks": result["forks_count"],
            "watchers": result["watchers_count"],
            "language": result.get("language", "Unknown"),
            "url": result["html_url"],
            "clone_url": result["clone_url"],
            "created_at": result["created_at"],
            "updated_at": result["updated_at"],
            "open_issues": result.get("open_issues_count", 0),
            "topics": result.get("topics", []),
            "license": result.get("license", {}).get("name", "No license"),
            "default_branch": result.get("default_branch", "main")
        }
    
    def list_issues(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        per_page: int = 30
    ) -> List[Dict[str, Any]]:
        """
        List issues for a repository.
        
        Args:
            owner: Repository owner username
            repo: Repository name
            state: Issue state (open, closed, all)
            per_page: Number of results per page
        
        Returns:
            List of issue dictionaries
        """
        params = {
            "state": state,
            "per_page": min(per_page, 100)
        }
        
        result = self._make_request("GET", f"/repos/{owner}/{repo}/issues", params=params)
        
        if not result:
            logger.info(f"No issues found for {owner}/{repo}")
            return []
        
        # Extract relevant information
        issues = []
        for item in result:
            # Skip pull requests (they appear in issues endpoint)
            if "pull_request" in item:
                continue
                
            issues.append({
                "number": item["number"],
                "title": item["title"],
                "state": item["state"],
                "body": item.get("body", "No description")[:200],  # Truncate long descriptions
                "user": item["user"]["login"],
                "labels": [label["name"] for label in item.get("labels", [])],
                "created_at": item["created_at"],
                "updated_at": item["updated_at"],
                "comments": item.get("comments", 0),
                "url": item["html_url"]
            })
        
        logger.info(f"Found {len(issues)} issues for {owner}/{repo}")
        return issues
    
    def create_issue(
        self,
        owner: str,
        repo: str,
        title: str,
        body: Optional[str] = None,
        labels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new issue in a repository.
        
        Args:
            owner: Repository owner username
            repo: Repository name
            title: Issue title
            body: Issue description
            labels: List of label names
        
        Returns:
            Created issue information
        """
        data = {
            "title": title,
        }
        
        if body:
            data["body"] = body
        
        if labels:
            data["labels"] = labels
        
        result = self._make_request("POST", f"/repos/{owner}/{repo}/issues", json=data)
        
        logger.info(f"Created issue #{result['number']} in {owner}/{repo}")
        
        return {
            "number": result["number"],
            "title": result["title"],
            "state": result["state"],
            "url": result["html_url"],
            "created_at": result["created_at"]
        }
