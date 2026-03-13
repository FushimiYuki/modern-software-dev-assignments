# Action Item Extractor

A FastAPI + SQLite application that intelligently extracts actionable items from free-form notes using both rule-based heuristics and AI-powered LLM extraction.

## Overview

This application provides two methods for extracting action items from text:

1. **Rule-Based Extraction**: Uses predefined heuristics to identify action items from structured formats (bullet points, checkboxes, numbered lists, keyword prefixes)
2. **LLM-Based Extraction**: Leverages Ollama's large language models (llama3.2) to intelligently extract action items from both structured and natural language text

The LLM approach excels at understanding context and extracting tasks from conversational text that rule-based methods would miss.

## Features

- ✅ Dual extraction methods (rule-based and AI-powered)
- 📝 Save notes to SQLite database
- ✓ Mark action items as complete
- 🔍 List and retrieve all saved notes
- 🧪 Comprehensive test suite
- 🎨 Clean, responsive web interface

## Technology Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: SQLite
- **AI/ML**: Ollama (llama3.2)
- **Package Management**: Poetry
- **Testing**: pytest
- **Frontend**: Vanilla JavaScript with HTML/CSS

## Prerequisites

- Python 3.10 or higher
- Poetry (Python package manager)
- Ollama (for LLM-based extraction)

## Installation

### 1. Set Up Python Environment

```bash
# Create a virtual environment
python3.11 -m venv venv

# Activate the virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install Poetry in the virtual environment
pip install --upgrade pip
pip install poetry
```

### 2. Install Dependencies

```bash
# From the project root directory
poetry install
```

### 3. Install and Set Up Ollama

```bash
# Install Ollama (macOS)
brew install ollama

# Download the llama3.2 model
ollama pull llama3.2:latest

# Start Ollama service (in a separate terminal)
ollama serve
```

## Running the Application

### Start the Server

```bash
# Activate virtual environment if not already activated
source venv/bin/activate

# Run the FastAPI server with auto-reload
poetry run uvicorn week2.app.main:app --reload
```

The server will start at `http://127.0.0.1:8000`

### Access the Application

Open your web browser and navigate to:
- **Web Interface**: http://127.0.0.1:8000
- **API Documentation**: http://127.0.0.1:8000/docs
- **Alternative API Docs**: http://127.0.0.1:8000/redoc

## API Endpoints

### Action Items

#### `POST /action-items/extract`
Extract action items using rule-based heuristics.

**Request Body:**
```json
{
  "text": "Meeting notes:\n- Call the client\n* Review designs",
  "save_note": true
}
```

**Response:**
```json
{
  "note_id": 1,
  "items": [
    {"id": 1, "text": "Call the client"},
    {"id": 2, "text": "Review designs"}
  ]
}
```

#### `POST /action-items/extract-llm`
Extract action items using AI-powered LLM.

**Request Body:**
```json
{
  "text": "We need to finalize the budget. Don't forget to call the client!",
  "save_note": true
}
```

**Response:**
```json
{
  "note_id": 2,
  "method": "llm",
  "items": [
    {"id": 3, "text": "Finalize the budget"},
    {"id": 4, "text": "Call the client"}
  ]
}
```

#### `GET /action-items`
List all action items, optionally filtered by note_id.

**Query Parameters:**
- `note_id` (optional): Filter by specific note

#### `POST /action-items/{action_item_id}/done`
Mark an action item as done or undone.

**Request Body:**
```json
{
  "done": true
}
```

### Notes

#### `POST /notes`
Create a new note.

**Request Body:**
```json
{
  "content": "Meeting notes from today..."
}
```

#### `GET /notes`
List all saved notes.

**Response:**
```json
[
  {
    "id": 1,
    "content": "Meeting notes...",
    "created_at": "2026-03-12T10:30:00"
  }
]
```

#### `GET /notes/{note_id}`
Retrieve a specific note by ID.

## Testing

### Run All Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run pytest
poetry run pytest week2/tests/ -v
```

### Run Specific Test Files

```bash
# Test extraction functions
poetry run pytest week2/tests/test_extract.py -v

# Test API integration
poetry run python week2/tests/test_api_integration.py
```

### Run Comparison Demo

```bash
# Visual comparison of rule-based vs LLM extraction
poetry run python week2/tests/comparison_demo.py
```

### Expected Test Results

All 12 unit tests should pass:
- ✅ Rule-based extraction tests (1 test)
- ✅ LLM extraction tests (9 tests)
- ✅ Comparison tests (2 tests)

## Project Structure

```
week2/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── db.py                # Database operations and schema
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── action_items.py  # Action item extraction endpoints
│   │   └── notes.py         # Notes CRUD endpoints
│   └── services/
│       └── extract.py       # Extraction logic (rule-based & LLM)
├── frontend/
│   └── index.html           # Web interface
├── tests/
│   ├── __init__.py
│   ├── test_extract.py      # Unit tests for extraction functions
│   ├── comparison_demo.py   # Demo script comparing methods
│   └── test_api_integration.py  # API endpoint tests
├── assignment.md            # Assignment instructions
└── writeup.md              # Assignment writeup

data/
└── actions.db              # SQLite database (created automatically)
```

## Usage Examples

### Web Interface

1. **Extract with Rules**: Paste text and click "Extract (Rule-Based)"
2. **Extract with AI**: Paste text and click "Extract (LLM) 🤖"
3. **View Notes**: Click "List All Notes" to see saved notes
4. **Mark Complete**: Check boxes next to items to mark them done

### Python API

```python
import requests

# Extract using LLM
response = requests.post(
    "http://127.0.0.1:8000/action-items/extract-llm",
    json={
        "text": "We should update the docs and fix the bug.",
        "save_note": True
    }
)
data = response.json()
print(f"Extracted {len(data['items'])} items")
```

## Key Differences: Rule-Based vs LLM

| Aspect | Rule-Based | LLM-Based |
|--------|-----------|-----------|
| **Structured formats** | ✅ Excellent | ✅ Excellent |
| **Natural language** | ❌ Poor | ✅ Excellent |
| **Speed** | ⚡ Very Fast | 🐌 Slower |
| **Consistency** | 🎯 100% | 🎲 ~95% |
| **Context understanding** | ❌ None | ✅ Strong |
| **Resource usage** | 💚 Minimal | 💛 Moderate |

### Example Comparison

**Input Text:**
```
Meeting notes:
- Review designs
We should also update the documentation and call the client tomorrow.
```

**Rule-Based Output:** (1 item)
- Review designs

**LLM Output:** (3 items)
- Review designs
- Update the documentation
- Call the client tomorrow

## Configuration

### LLM Settings

Edit `week2/app/services/extract.py` to customize:

```python
# Change the model
model="llama3.2:latest"  # Try: llama3.1:8b, mistral, etc.

# Adjust temperature (0.0-1.0)
temperature=0.3  # Lower = more consistent, Higher = more creative
```

### Database Location

The SQLite database is stored at `data/actions.db` relative to the project root.

## Troubleshooting

### Ollama Connection Issues

```bash
# Check if Ollama is running
ps aux | grep ollama

# Start Ollama if not running
ollama serve
```

### Port Already in Use

```bash
# Use a different port
poetry run uvicorn week2.app.main:app --reload --port 8001
```

### Import Errors

```bash
# Ensure you're in the project root and virtual environment is activated
cd /path/to/modern-software-dev-assignments
source venv/bin/activate
```

## Development

### Adding New Extraction Methods

1. Add function to `week2/app/services/extract.py`
2. Create endpoint in `week2/app/routers/action_items.py`
3. Add tests in `week2/tests/test_extract.py`
4. Update frontend in `week2/frontend/index.html`

### Database Schema

The application automatically creates tables on first run:

**notes** table:
- `id` (INTEGER PRIMARY KEY)
- `content` (TEXT)
- `created_at` (TEXT)

**action_items** table:
- `id` (INTEGER PRIMARY KEY)
- `note_id` (INTEGER, nullable)
- `text` (TEXT)
- `done` (INTEGER)
- `created_at` (TEXT)

## License

This is a course assignment project for Modern Software Development.

## Acknowledgments

- FastAPI for the excellent web framework
- Ollama for local LLM inference
- llama3.2 model for intelligent text understanding
