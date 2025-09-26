#!/usr/bin/env python3
"""
Test script for natural language analysis functionality
"""

import json
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(__file__))

from core.gemini_analysis import generate_natural_language_report

def test_with_sample_data():
    # Load the existing sample data
    try:
        with open('temp/output.txt', 'r', encoding='utf-8') as f:
            sample_data = json.load(f)
    except Exception as e:
        print(f"Error loading sample data: {e}")
        return
    
    print("=== Testing Natural Language Analysis ===\n")
    print(f"Product: {sample_data.get('title', 'Unknown')}")
    print(f"Current Compliance Score: {sample_data.get('compliance_summary', {}).get('compliance_score', '0/4')}\n")
    
    # Test the natural language analysis function
    try:
        result = generate_natural_language_report(sample_data)
        
        print("=== ANALYSIS RESULT ===")
        print(f"Gemini Enhanced: {result.get('gemini_enhanced', False)}")
        if result.get('gemini_error'):
            print(f"Gemini Error: {result['gemini_error']}")
        
        print("\n=== FINAL REPORT ===")
        print(result.get('final_report', 'No report generated'))
        
        if result.get('static_analysis', {}).get('summary'):
            summary = result['static_analysis']['summary']
            print(f"\n=== SUMMARY ===")
            print(f"Compliance Level: {summary.get('compliance_level')}")
            print(f"Confidence: {summary.get('confidence')}")
            print(f"Key Strengths: {summary.get('key_strengths', [])}")
            print(f"Priority Issues: {summary.get('priority_issues', [])}")
        
    except Exception as e:
        print(f"Error testing natural language analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_with_sample_data()