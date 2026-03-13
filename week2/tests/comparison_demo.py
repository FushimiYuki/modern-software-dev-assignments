#!/usr/bin/env python3
"""
Comparison demonstration script for rule-based vs LLM-based extraction.
This is a demo script, not automated tests (those are in test_extract.py)
"""

import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from week2.app.services.extract import extract_action_items, extract_action_items_llm


# Test cases with different formats
test_cases = [
    {
        "name": "Bullet Points",
        "text": """
- Buy groceries
* Call the dentist
• Schedule team meeting
        """
    },
    {
        "name": "Mixed Format",
        "text": """
Meeting notes from today:
- Need to call the client tomorrow
* Review the design mockups
We should also update the documentation and fix the bug in production.
TODO: Schedule the team meeting
        """
    },
    {
        "name": "Checkboxes",
        "text": """
Sprint planning:
[ ] Implement login feature
[ ] Write unit tests
[todo] Review pull requests
        """
    },
    {
        "name": "Natural Language",
        "text": """
After the meeting, we need to finalize the budget proposal. 
John will contact the vendor about pricing.
Remember to send the report to the client by Friday.
        """
    },
    {
        "name": "Numbered List",
        "text": """
1. Create the database schema
2. Implement API endpoints
3. Write documentation
4. Deploy to staging
        """
    },
    {
        "name": "Empty Input",
        "text": ""
    }
]


def print_comparison(test_name: str, text: str):
    """Print comparison between rule-based and LLM extraction"""
    print("=" * 80)
    print(f"TEST: {test_name}")
    print("=" * 80)
    print(f"\nInput Text:\n{text}\n")
    
    print("-" * 80)
    print("Rule-Based Extraction:")
    print("-" * 80)
    rule_based = extract_action_items(text)
    if rule_based:
        for i, item in enumerate(rule_based, 1):
            print(f"  {i}. {item}")
    else:
        print("  (No items found)")
    
    print("\n" + "-" * 80)
    print("LLM-Based Extraction:")
    print("-" * 80)
    try:
        llm_based = extract_action_items_llm(text)
        if llm_based:
            for i, item in enumerate(llm_based, 1):
                print(f"  {i}. {item}")
        else:
            print("  (No items found)")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    print("\n")


def main():
    print("\n" + "=" * 80)
    print("ACTION ITEM EXTRACTION COMPARISON DEMO")
    print("Rule-Based vs LLM-Based Approaches")
    print("=" * 80 + "\n")
    
    for test_case in test_cases:
        print_comparison(test_case["name"], test_case["text"])
    
    print("=" * 80)
    print("DEMO COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()
