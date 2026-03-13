import os
import pytest

from ..app.services.extract import extract_action_items, extract_action_items_llm


def test_extract_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


# ==================== LLM-based extraction tests ====================


def test_llm_extract_simple_bullets():
    """Test LLM extraction with simple bullet points"""
    text = """
- Buy groceries
* Call the dentist
• Schedule team meeting
    """
    items = extract_action_items_llm(text)
    
    assert len(items) == 3
    assert any("groceries" in item.lower() for item in items)
    assert any("dentist" in item.lower() for item in items)
    assert any("meeting" in item.lower() for item in items)


def test_llm_extract_checkboxes():
    """Test LLM extraction with checkbox format"""
    text = """
Sprint planning:
[ ] Implement login feature
[ ] Write unit tests
[todo] Review pull requests
    """
    items = extract_action_items_llm(text)
    
    assert len(items) == 3
    assert any("login" in item.lower() for item in items)
    assert any("unit tests" in item.lower() or "test" in item.lower() for item in items)
    assert any("pull request" in item.lower() for item in items)


def test_llm_extract_natural_language():
    """Test LLM extraction with natural language (key advantage over rule-based)"""
    text = """
After the meeting, we need to finalize the budget proposal. 
John will contact the vendor about pricing.
Remember to send the report to the client by Friday.
    """
    items = extract_action_items_llm(text)
    
    # LLM should extract at least 2 items from natural language
    assert len(items) >= 2
    assert any("budget" in item.lower() or "finalize" in item.lower() for item in items)
    assert any("report" in item.lower() or "send" in item.lower() for item in items)


def test_llm_extract_mixed_format():
    """Test LLM extraction with mixed structured and natural language"""
    text = """
Meeting notes from today:
- Need to call the client tomorrow
* Review the design mockups
We should also update the documentation and fix the bug in production.
TODO: Schedule the team meeting
    """
    items = extract_action_items_llm(text)
    
    # LLM should extract more items than rule-based (including natural language tasks)
    assert len(items) >= 4
    assert any("client" in item.lower() for item in items)
    assert any("mockup" in item.lower() or "design" in item.lower() for item in items)
    assert any("documentation" in item.lower() for item in items)
    assert any("meeting" in item.lower() for item in items)


def test_llm_extract_numbered_list():
    """Test LLM extraction with numbered lists"""
    text = """
1. Create the database schema
2. Implement API endpoints
3. Write documentation
4. Deploy to staging
    """
    items = extract_action_items_llm(text)
    
    assert len(items) == 4
    assert any("database" in item.lower() or "schema" in item.lower() for item in items)
    assert any("api" in item.lower() or "endpoint" in item.lower() for item in items)
    assert any("documentation" in item.lower() for item in items)
    assert any("deploy" in item.lower() or "staging" in item.lower() for item in items)


def test_llm_extract_empty_input():
    """Test LLM extraction with empty input"""
    text = ""
    items = extract_action_items_llm(text)
    assert items == []
    
    text = "   \n\n  "
    items = extract_action_items_llm(text)
    assert items == []


def test_llm_extract_no_action_items():
    """Test LLM extraction when text contains no clear action items"""
    text = """
This is just a description of what happened.
The weather was nice and everyone enjoyed the event.
It was a great experience overall.
    """
    items = extract_action_items_llm(text)
    # Should return empty or very few items
    assert len(items) <= 1


def test_llm_extract_keyword_prefixes():
    """Test LLM extraction with keyword prefixes like TODO, ACTION"""
    text = """
TODO: Finish the report
Action: Contact stakeholders
Next: Review feedback
    """
    items = extract_action_items_llm(text)
    
    # LLM should extract at least 2 items (may interpret "Next:" differently)
    assert len(items) >= 2
    assert any("report" in item.lower() for item in items)
    assert any("stakeholder" in item.lower() or "contact" in item.lower() for item in items)
    # LLM should remove prefixes
    assert not any(item.startswith("TODO:") for item in items)
    assert not any(item.startswith("Action:") for item in items)


def test_llm_extract_deduplication():
    """Test that LLM removes duplicate action items"""
    text = """
- Buy groceries
* Buy groceries
1. Buy groceries
    """
    items = extract_action_items_llm(text)
    
    # Should deduplicate similar items
    assert len(items) <= 2  # Allow some variation in how LLM handles this


# ==================== Comparison tests ====================


def test_comparison_structured_format():
    """Compare rule-based and LLM on structured formats (should be similar)"""
    text = """
- Task one
* Task two
• Task three
    """
    rule_items = extract_action_items(text)
    llm_items = extract_action_items_llm(text)
    
    # Both should extract 3 items
    assert len(rule_items) == 3
    assert len(llm_items) == 3


def test_comparison_natural_language():
    """Compare rule-based and LLM on natural language (LLM should be better)"""
    text = """
We need to update the website content.
Don't forget to send the invoice.
John will prepare the presentation.
    """
    rule_items = extract_action_items(text)
    llm_items = extract_action_items_llm(text)
    
    # LLM should extract more items from natural language
    assert len(llm_items) >= len(rule_items)
    # LLM should find at least 2 action items
    assert len(llm_items) >= 2
