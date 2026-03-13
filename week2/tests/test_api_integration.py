#!/usr/bin/env python3
"""
Test script to verify the new API endpoints work correctly
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_llm_extraction():
    """Test the LLM extraction endpoint"""
    print("\n" + "="*80)
    print("Testing LLM Extraction Endpoint")
    print("="*80)
    
    test_text = """
Meeting notes:
- Review the design mockups
We should also update the documentation and fix the bug in production.
Don't forget to call the client tomorrow!
    """
    
    payload = {
        "text": test_text,
        "save_note": True
    }
    
    print("\nSending request to /action-items/extract-llm...")
    try:
        response = requests.post(
            f"{BASE_URL}/action-items/extract-llm",
            json=payload
        )
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ Success! Status Code: {response.status_code}")
        print(f"\nNote ID: {data.get('note_id')}")
        print(f"Method: {data.get('method', 'N/A')}")
        print(f"\nExtracted Items ({len(data['items'])}):")
        for i, item in enumerate(data['items'], 1):
            print(f"  {i}. {item['text']} (ID: {item['id']})")
        
        return data.get('note_id')
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return None


def test_list_notes():
    """Test the list all notes endpoint"""
    print("\n" + "="*80)
    print("Testing List All Notes Endpoint")
    print("="*80)
    
    print("\nSending request to /notes...")
    try:
        response = requests.get(f"{BASE_URL}/notes")
        response.raise_for_status()
        notes = response.json()
        
        print(f"✅ Success! Status Code: {response.status_code}")
        print(f"\nTotal Notes: {len(notes)}")
        
        if notes:
            print("\nRecent Notes:")
            for note in notes[:5]:  # Show first 5 notes
                preview = note['content'][:100] + "..." if len(note['content']) > 100 else note['content']
                print(f"\n  ID: {note['id']}")
                print(f"  Created: {note['created_at']}")
                print(f"  Content: {preview}")
        else:
            print("\n  (No notes found)")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")


def test_rule_based_extraction():
    """Test the original rule-based extraction for comparison"""
    print("\n" + "="*80)
    print("Testing Rule-Based Extraction (for comparison)")
    print("="*80)
    
    test_text = """
- Review the design mockups
We should also update the documentation.
    """
    
    payload = {
        "text": test_text,
        "save_note": False
    }
    
    print("\nSending request to /action-items/extract...")
    try:
        response = requests.post(
            f"{BASE_URL}/action-items/extract",
            json=payload
        )
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ Success! Status Code: {response.status_code}")
        print(f"\nExtracted Items ({len(data['items'])}):")
        for i, item in enumerate(data['items'], 1):
            print(f"  {i}. {item['text']}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")


def main():
    print("\n" + "="*80)
    print("API INTEGRATION TESTS")
    print("Testing new endpoints: extract-llm and list all notes")
    print("="*80)
    
    # Test LLM extraction
    test_llm_extraction()
    
    # Test listing notes
    test_list_notes()
    
    # Test rule-based for comparison
    test_rule_based_extraction()
    
    print("\n" + "="*80)
    print("TESTS COMPLETED")
    print("="*80)
    print(f"\n💡 You can now visit http://127.0.0.1:8000 to test the UI!")
    print("   - Try the 'Extract (LLM) 🤖' button for AI-powered extraction")
    print("   - Click 'List All Notes' to see all saved notes")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
