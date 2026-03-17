# GitHub MCP Server

A Model Context Protocol (MCP) server that provides tools to interact with GitHub's API. This server enables AI assistants to search repositories, get repository information, manage issues, and more.

## 🌟 Features

- **Repository Search**: Search GitHub repositories with advanced query support
- **Repository Information**: Get detailed information about any repository
- **Issue Management**: List and create issues in repositories
- **Rate Limit Handling**: Automatic handling of GitHub API rate limits
- **Error Resilience**: Robust error handling with retries and meaningful error messages
- **Comprehensive Logging**: Detailed logging for debugging and monitoring

## 📋 Prerequisites

- Python 3.10 or higher
- A GitHub account
- GitHub Personal Access Token (PAT)

## 🚀 Installation

### 1. Clone the Repository

```bash
cd week3
```

### 2. Install Dependencies

#### Using pip:
```bash
pip install -r requirements.txt
```

#### Or using the project's Poetry environment:
```bash
cd ..
source venv/bin/activate
pip install -r week3/requirements.txt
```

### 3. Get a GitHub Personal Access Token

1. Go to GitHub Settings: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a descriptive name (e.g., "MCP Server")
4. Select scopes:
   - `repo` - For full repository access (recommended)
   - Or `public_repo` - For public repositories only
5. Click "Generate token" and **copy the token immediately**

### 4. Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your GitHub token
nano .env  # or use your preferred editor
```

Update the `.env` file:
```bash
GITHUB_TOKEN=your_actual_github_token_here
```

## 🎮 Usage

### Running Locally (STDIO Transport)

The server uses STDIO transport for communication with MCP clients like Claude Desktop.

```bash
# From the week3 directory
python -m server.main
```

### Configuring with Claude Desktop

Add this configuration to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "github": {
      "command": "python",
      "args": [
        "-m",
        "server.main"
      ],
      "cwd": "/absolute/path/to/modern-software-dev-assignments/week3",
      "env": {
        "GITHUB_TOKEN": "your_github_token_here"
      }
    }
  }
}
```

**Important**: Replace `/absolute/path/to/` with the actual absolute path to your project directory.

### Configuring with Cursor

If using Cursor IDE with MCP support, add similar configuration to Cursor's MCP settings.

## 🔧 Available Tools

### 1. search_repositories

Search for GitHub repositories using a query string.

**Parameters:**
- `query` (required): Search query with optional qualifiers
- `sort` (optional): Sort field - `stars`, `forks`, `help-wanted-issues`, or `updated` (default: `stars`)
- `order` (optional): Sort order - `asc` or `desc` (default: `desc`)
- `per_page` (optional): Number of results (1-100, default: 10)

**Example queries:**
- `"fastapi"` - Simple search
- `"language:python stars:>5000"` - Python repos with 5000+ stars
- `"machine learning in:description"` - Repos with "machine learning" in description

**Example usage in Claude:**
```
Can you search for popular Python web frameworks on GitHub?
```

**Expected output:**
```
Found 10 repositories:

1. **fastapi/fastapi**
   Description: FastAPI framework, high performance, easy to learn...
   ⭐ 70000 stars | 🍴 5900 forks | 📝 Python | 🐛 125 issues
   URL: https://github.com/fastapi/fastapi
   Topics: fastapi, python, api, web-framework

...
```

### 2. get_repository_info

Get detailed information about a specific repository.

**Parameters:**
- `owner` (required): Repository owner (username or organization)
- `repo` (required): Repository name

**Example usage in Claude:**
```
Tell me about the fastapi/fastapi repository
```

**Expected output:**
```
# fastapi/fastapi

FastAPI framework, high performance, easy to learn, fast to code, ready for production

**Statistics:**
- ⭐ Stars: 70000
- 🍴 Forks: 5900
- 👁️ Watchers: 1200
- 🐛 Open Issues: 125

**Details:**
- Language: Python
- License: MIT License
- Default Branch: master
- Created: 2018-12-05T13:51:16Z
- Last Updated: 2024-01-15T10:30:00Z

**Topics:** fastapi, python, api, web-framework, async

**URLs:**
- Repository: https://github.com/fastapi/fastapi
- Clone: https://github.com/fastapi/fastapi.git
```

### 3. list_issues

List issues for a repository.

**Parameters:**
- `owner` (required): Repository owner
- `repo` (required): Repository name
- `state` (optional): Issue state - `open`, `closed`, or `all` (default: `open`)
- `per_page` (optional): Number of results (1-100, default: 30)

**Example usage in Claude:**
```
Show me the open issues in fastapi/fastapi
```

**Expected output:**
```
Found 125 issues for fastapi/fastapi:

**#1234**: Add support for WebSocket compression
   State: open | Author: @username | 💬 5 comments
   Labels: enhancement, websocket
   Created: 2024-01-10T14:23:00Z
   URL: https://github.com/fastapi/fastapi/issues/1234
   Description: It would be great if FastAPI could support...

...
```

### 4. create_issue

Create a new issue in a repository (requires write permissions).

**Parameters:**
- `owner` (required): Repository owner
- `repo` (required): Repository name
- `title` (required): Issue title
- `body` (optional): Issue description (supports Markdown)
- `labels` (optional): Array of label names

**Example usage in Claude:**
```
Create an issue in my test repository about adding documentation
```

**Expected output:**
```
✅ Successfully created issue!

**#42**: Add documentation for API endpoints
State: open
Created: 2024-01-15T10:30:00Z
URL: https://github.com/username/test-repo/issues/42
```

## 🧪 Testing

### Run Unit Tests

```bash
# Install test dependencies
pip install pytest pytest-mock

# Run tests
cd week3
python -m pytest tests/ -v
```

### Manual Testing

You can test the GitHub API wrapper independently:

```python
from server.config import Config
from server.github_api import GitHubAPI

# Initialize
config = Config.from_env()
github = GitHubAPI(config)

# Test search
results = github.search_repositories("fastapi", per_page=5)
print(f"Found {len(results)} repositories")

# Test repository info
repo = github.get_repository("fastapi", "fastapi")
print(f"{repo['name']}: {repo['stars']} stars")
```

## 📊 Error Handling

The server handles various error conditions gracefully:

### Rate Limiting
```
⚠️ GitHub API rate limit exceeded: Resets at 2024-01-15 11:00:00
```

### Authentication Errors
```
❌ GitHub API error: Authentication failed. Check your GitHub token
```

### Resource Not Found
```
❌ GitHub API error: Resource not found
```

### Network Errors
```
❌ GitHub API error: Failed to connect to GitHub API
```

### Timeout
```
❌ GitHub API error: Request timed out after 30 seconds
```

## 🔐 Security Best Practices

1. **Never commit your `.env` file** - It contains your GitHub token
2. **Use a token with minimal required permissions**
3. **Rotate your token periodically**
4. **For public repositories, use `public_repo` scope instead of `repo`**
5. **Set token expiration when creating it**

## 📁 Project Structure

```
week3/
├── server/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # MCP server implementation
│   ├── github_api.py        # GitHub API wrapper
│   └── config.py            # Configuration management
├── tests/
│   ├── __init__.py
│   └── test_server.py       # Unit tests
├── .env.example             # Environment variables template
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🐛 Troubleshooting

### "GITHUB_TOKEN environment variable is required"

**Solution**: Make sure you've created a `.env` file with your GitHub token, or export it in your shell:
```bash
export GITHUB_TOKEN=your_token_here
```

### "Authentication failed"

**Solutions**:
1. Verify your token is correct
2. Check that the token hasn't expired
3. Ensure the token has the required permissions

### "Rate limit exceeded"

**Solutions**:
1. Wait until the rate limit resets (time shown in error message)
2. Use authenticated requests (they have higher rate limits)
3. Reduce the frequency of requests

### Server not showing in Claude Desktop

**Solutions**:
1. Restart Claude Desktop after updating config
2. Check the logs in Claude Desktop's developer tools
3. Verify the `cwd` path is absolute and correct
4. Ensure Python is in your PATH

## 🚀 Extra Credit Features

### Implemented:
- ✅ Comprehensive error handling with specific error types
- ✅ Rate limit detection and warnings
- ✅ Retry logic with exponential backoff
- ✅ Structured logging to stderr (not stdout)
- ✅ Input validation for all tools
- ✅ Detailed documentation

### Potential Enhancements (Not Implemented):
- Remote HTTP transport deployment
- OAuth2 authentication flow
- Webhook support
- GitHub GraphQL API integration

## 📚 References

- [MCP Server Quickstart](https://modelcontextprotocol.io/quickstart/server)
- [GitHub REST API Documentation](https://docs.github.com/en/rest)
- [MCP Specification](https://modelcontextprotocol.io/specification)
- [GitHub Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)

## 📝 Development Notes

### Code Quality
- Type hints throughout the codebase
- Descriptive variable and function names
- Modular design with separation of concerns
- Comprehensive docstrings

### Reliability Features
- Automatic retry with backoff for transient failures
- Rate limit awareness and warnings
- Timeout handling
- Connection error handling
- HTTP status code handling

### Logging
All logs go to stderr (not stdout) to avoid interfering with MCP communication:
- INFO: Normal operations
- WARNING: Rate limit warnings, recoverable issues
- ERROR: API failures, exceptions

## 📄 License

This is a course assignment project for Modern Software Development.

## 🙏 Acknowledgments

- Model Context Protocol (MCP) team
- GitHub REST API
- FastAPI and Python community
