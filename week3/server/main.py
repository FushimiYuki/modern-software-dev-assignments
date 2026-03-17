#!/usr/bin/env python3
"""
GitHub MCP Server

A Model Context Protocol server that provides tools to interact with GitHub's API.
"""

import asyncio
import logging
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    TextContent,
    Tool,
    INVALID_PARAMS,
    INTERNAL_ERROR,
)

from .config import Config
from .github_api import GitHubAPI, GitHubAPIError, RateLimitError

# Configure logging to stderr (not stdout, which is used for MCP communication)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr
)

logger = logging.getLogger(__name__)

# Initialize configuration and GitHub API client
config = Config.from_env()
github_api = GitHubAPI(config)

# Create MCP server
app = Server("github-mcp-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    List available tools.
    Each tool represents a GitHub API operation.
    """
    return [
        Tool(
            name="search_repositories",
            description=(
                "Search for GitHub repositories using a query string. "
                "Supports advanced search qualifiers like 'language:python stars:>1000'. "
                "Returns repository name, description, stars, forks, language, and URL."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "Search query. Examples: 'fastapi', 'language:python stars:>5000', "
                            "'machine learning in:description'"
                        )
                    },
                    "sort": {
                        "type": "string",
                        "description": "Sort field: stars, forks, help-wanted-issues, or updated",
                        "enum": ["stars", "forks", "help-wanted-issues", "updated"],
                        "default": "stars"
                    },
                    "order": {
                        "type": "string",
                        "description": "Sort order: asc or desc",
                        "enum": ["asc", "desc"],
                        "default": "desc"
                    },
                    "per_page": {
                        "type": "integer",
                        "description": "Number of results to return (1-100)",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_repository_info",
            description=(
                "Get detailed information about a specific GitHub repository. "
                "Returns stars, forks, language, license, topics, and more."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {
                        "type": "string",
                        "description": "Repository owner (username or organization)"
                    },
                    "repo": {
                        "type": "string",
                        "description": "Repository name"
                    }
                },
                "required": ["owner", "repo"]
            }
        ),
        Tool(
            name="list_issues",
            description=(
                "List issues for a GitHub repository. "
                "Can filter by state (open, closed, all)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {
                        "type": "string",
                        "description": "Repository owner (username or organization)"
                    },
                    "repo": {
                        "type": "string",
                        "description": "Repository name"
                    },
                    "state": {
                        "type": "string",
                        "description": "Issue state filter",
                        "enum": ["open", "closed", "all"],
                        "default": "open"
                    },
                    "per_page": {
                        "type": "integer",
                        "description": "Number of results to return (1-100)",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 30
                    }
                },
                "required": ["owner", "repo"]
            }
        ),
        Tool(
            name="create_issue",
            description=(
                "Create a new issue in a GitHub repository. "
                "Requires write permissions to the repository."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {
                        "type": "string",
                        "description": "Repository owner (username or organization)"
                    },
                    "repo": {
                        "type": "string",
                        "description": "Repository name"
                    },
                    "title": {
                        "type": "string",
                        "description": "Issue title"
                    },
                    "body": {
                        "type": "string",
                        "description": "Issue description (supports Markdown)"
                    },
                    "labels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of label names to add to the issue"
                    }
                },
                "required": ["owner", "repo", "title"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """
    Handle tool calls.
    Each tool corresponds to a GitHub API operation.
    """
    try:
        logger.info(f"Tool called: {name} with arguments: {arguments}")
        
        if name == "search_repositories":
            # Validate required parameters
            if not arguments.get("query"):
                return [TextContent(
                    type="text",
                    text="Error: 'query' parameter is required"
                )]
            
            # Call GitHub API
            results = github_api.search_repositories(
                query=arguments["query"],
                sort=arguments.get("sort", "stars"),
                order=arguments.get("order", "desc"),
                per_page=arguments.get("per_page", 10)
            )
            
            # Format results
            if not results:
                return [TextContent(
                    type="text",
                    text=f"No repositories found for query: {arguments['query']}"
                )]
            
            output = f"Found {len(results)} repositories:\n\n"
            for i, repo in enumerate(results, 1):
                output += f"{i}. **{repo['name']}**\n"
                output += f"   Description: {repo['description']}\n"
                output += f"   ⭐ {repo['stars']} stars | 🍴 {repo['forks']} forks | "
                output += f"📝 {repo['language']} | 🐛 {repo['open_issues']} issues\n"
                output += f"   URL: {repo['url']}\n"
                if repo['topics']:
                    output += f"   Topics: {', '.join(repo['topics'])}\n"
                output += "\n"
            
            return [TextContent(type="text", text=output)]
        
        elif name == "get_repository_info":
            # Validate required parameters
            if not arguments.get("owner") or not arguments.get("repo"):
                return [TextContent(
                    type="text",
                    text="Error: 'owner' and 'repo' parameters are required"
                )]
            
            # Call GitHub API
            repo = github_api.get_repository(
                owner=arguments["owner"],
                repo=arguments["repo"]
            )
            
            # Format results
            output = f"# {repo['name']}\n\n"
            output += f"{repo['description']}\n\n"
            output += f"**Statistics:**\n"
            output += f"- ⭐ Stars: {repo['stars']}\n"
            output += f"- 🍴 Forks: {repo['forks']}\n"
            output += f"- 👁️ Watchers: {repo['watchers']}\n"
            output += f"- 🐛 Open Issues: {repo['open_issues']}\n\n"
            output += f"**Details:**\n"
            output += f"- Language: {repo['language']}\n"
            output += f"- License: {repo['license']}\n"
            output += f"- Default Branch: {repo['default_branch']}\n"
            output += f"- Created: {repo['created_at']}\n"
            output += f"- Last Updated: {repo['updated_at']}\n\n"
            if repo['topics']:
                output += f"**Topics:** {', '.join(repo['topics'])}\n\n"
            output += f"**URLs:**\n"
            output += f"- Repository: {repo['url']}\n"
            output += f"- Clone: {repo['clone_url']}\n"
            
            return [TextContent(type="text", text=output)]
        
        elif name == "list_issues":
            # Validate required parameters
            if not arguments.get("owner") or not arguments.get("repo"):
                return [TextContent(
                    type="text",
                    text="Error: 'owner' and 'repo' parameters are required"
                )]
            
            # Call GitHub API
            issues = github_api.list_issues(
                owner=arguments["owner"],
                repo=arguments["repo"],
                state=arguments.get("state", "open"),
                per_page=arguments.get("per_page", 30)
            )
            
            # Format results
            if not issues:
                state = arguments.get("state", "open")
                return [TextContent(
                    type="text",
                    text=f"No {state} issues found for {arguments['owner']}/{arguments['repo']}"
                )]
            
            output = f"Found {len(issues)} issues for {arguments['owner']}/{arguments['repo']}:\n\n"
            for issue in issues:
                output += f"**#{issue['number']}**: {issue['title']}\n"
                output += f"   State: {issue['state']} | Author: @{issue['user']} | "
                output += f"💬 {issue['comments']} comments\n"
                if issue['labels']:
                    output += f"   Labels: {', '.join(issue['labels'])}\n"
                output += f"   Created: {issue['created_at']}\n"
                output += f"   URL: {issue['url']}\n"
                if issue['body']:
                    output += f"   Description: {issue['body']}...\n"
                output += "\n"
            
            return [TextContent(type="text", text=output)]
        
        elif name == "create_issue":
            # Validate required parameters
            if not all(k in arguments for k in ["owner", "repo", "title"]):
                return [TextContent(
                    type="text",
                    text="Error: 'owner', 'repo', and 'title' parameters are required"
                )]
            
            # Call GitHub API
            issue = github_api.create_issue(
                owner=arguments["owner"],
                repo=arguments["repo"],
                title=arguments["title"],
                body=arguments.get("body"),
                labels=arguments.get("labels")
            )
            
            # Format results
            output = f"✅ Successfully created issue!\n\n"
            output += f"**#{issue['number']}**: {issue['title']}\n"
            output += f"State: {issue['state']}\n"
            output += f"Created: {issue['created_at']}\n"
            output += f"URL: {issue['url']}\n"
            
            return [TextContent(type="text", text=output)]
        
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    
    except RateLimitError as e:
        logger.error(f"Rate limit error: {e}")
        return [TextContent(
            type="text",
            text=f"⚠️ GitHub API rate limit exceeded: {str(e)}"
        )]
    
    except GitHubAPIError as e:
        logger.error(f"GitHub API error: {e}")
        return [TextContent(
            type="text",
            text=f"❌ GitHub API error: {str(e)}"
        )]
    
    except Exception as e:
        logger.error(f"Unexpected error in {name}: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=f"❌ Unexpected error: {str(e)}"
        )]


async def main():
    """Run the MCP server using stdio transport."""
    logger.info("Starting GitHub MCP Server...")
    
    try:
        # Validate configuration
        config.validate()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        logger.info("Server running on stdio transport")
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
