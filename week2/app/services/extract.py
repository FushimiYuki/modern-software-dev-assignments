from __future__ import annotations

import os
import re
from typing import List
import json
from typing import Any
from ollama import chat
from dotenv import load_dotenv

load_dotenv()

BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
KEYWORD_PREFIXES = (
    "todo:",
    "action:",
    "next:",
)


def _is_action_line(line: str) -> bool:
    stripped = line.strip().lower()
    if not stripped:
        return False
    if BULLET_PREFIX_PATTERN.match(stripped):
        return True
    if any(stripped.startswith(prefix) for prefix in KEYWORD_PREFIXES):
        return True
    if "[ ]" in stripped or "[todo]" in stripped:
        return True
    return False


def extract_action_items(text: str) -> List[str]:
    lines = text.splitlines()
    extracted: List[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if _is_action_line(line):
            cleaned = BULLET_PREFIX_PATTERN.sub("", line)
            cleaned = cleaned.strip()
            # Trim common checkbox markers
            cleaned = cleaned.removeprefix("[ ]").strip()
            cleaned = cleaned.removeprefix("[todo]").strip()
            extracted.append(cleaned)
    # Fallback: if nothing matched, heuristically split into sentences and pick imperative-like ones
    if not extracted:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            s = sentence.strip()
            if not s:
                continue
            if _looks_imperative(s):
                extracted.append(s)
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: List[str] = []
    for item in extracted:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(item)
    return unique


def _looks_imperative(sentence: str) -> bool:
    words = re.findall(r"[A-Za-z']+", sentence)
    if not words:
        return False
    first = words[0]
    # Crude heuristic: treat these as imperative starters
    imperative_starters = {
        "add",
        "create",
        "implement",
        "fix",
        "update",
        "write",
        "check",
        "verify",
        "refactor",
        "document",
        "design",
        "investigate",
    }
    return first.lower() in imperative_starters


def extract_action_items_llm(text: str) -> List[str]:
    """
    Extract action items from text using Ollama LLM.
    
    This function uses a large language model to intelligently identify and extract
    action items from free-form text, providing more flexibility than rule-based approaches.
    
    Args:
        text: The input text to extract action items from
        
    Returns:
        A list of extracted action items as strings
    """
    if not text or not text.strip():
        return []
    
    # Define the schema for structured output
    schema = {
        "type": "object",
        "properties": {
            "action_items": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "List of action items extracted from the text"
            }
        },
        "required": ["action_items"]
    }
    
    # Craft the prompt for the LLM
    prompt = f"""You are an AI assistant specialized in extracting action items from text.

Given the following text, identify and extract all action items, tasks, or to-dos mentioned.

Rules:
- Extract concrete, actionable tasks
- Look for tasks in bullet points, checkboxes ([ ]), numbered lists, or natural language
- Remove bullet points, checkboxes, and prefixes (like "TODO:", "Action:", "[todo]", "[ ]", etc.)
- Keep the core action description
- If multiple similar items exist, keep only unique ones
- Return items in a clean, concise format
- Even if the text seems short or simple, extract all tasks mentioned
- If no action items are found, return an empty list

Text:
{text}

Extract all action items and return them as a JSON array."""

    try:
        # Call Ollama with structured output
        response = chat(
            model="llama3.2:latest",  # Using a lightweight model; can be changed to larger models
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            format=schema,  # Enable structured output with JSON schema
            options={
                "temperature": 0.3,  # Lower temperature for more consistent extraction
            }
        )
        
        # Parse the response
        content = response.message.content
        
        # Handle if content is already a dict or needs JSON parsing
        if isinstance(content, str):
            result = json.loads(content)
        else:
            result = content
            
        action_items = result.get("action_items", [])
        
        # Additional cleanup: ensure all items are strings and non-empty
        cleaned_items = [
            item.strip() 
            for item in action_items 
            if isinstance(item, str) and item.strip()
        ]
        
        return cleaned_items
        
    except Exception as e:
        # Fallback to rule-based extraction if LLM fails
        print(f"Warning: LLM extraction failed with error: {e}")
        print("Falling back to rule-based extraction...")
        return extract_action_items(text)