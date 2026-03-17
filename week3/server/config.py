"""
Configuration management for the GitHub MCP Server.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Configuration for GitHub API integration."""
    
    github_token: Optional[str] = None
    github_api_base_url: str = "https://api.github.com"
    timeout: int = 30
    max_retries: int = 3
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        return cls(
            github_token=os.getenv("GITHUB_TOKEN"),
            github_api_base_url=os.getenv("GITHUB_API_BASE_URL", "https://api.github.com"),
            timeout=int(os.getenv("GITHUB_API_TIMEOUT", "30")),
            max_retries=int(os.getenv("GITHUB_API_MAX_RETRIES", "3")),
        )
    
    def validate(self) -> None:
        """Validate required configuration."""
        if not self.github_token:
            raise ValueError(
                "GITHUB_TOKEN environment variable is required. "
                "Get one at https://github.com/settings/tokens"
            )
