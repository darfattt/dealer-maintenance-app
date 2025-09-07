#!/usr/bin/env python3
"""
Test script for SentimentAnalysisService to debug API timeout issues
"""

import asyncio
import logging
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.sentiment_analysis_service import SentimentAnalysisService

# Configure logging to see debug information
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_sentiment_analysis():
    """Test the sentiment analysis service with sample data"""
    print("🚀 Starting SentimentAnalysisService test...")
    
    # Initialize the service
    service = SentimentAnalysisService()
    
    # Test data matching your Postman request
    test_records = [
        {
            "id": "26947de5-41d8-4b7c-8708-d20330ed07d6",
            "no_tiket": "#421491",
            "review": "Tidak dapat potongan Voucher"
        },
        {
            "id": "36947de5-41d8-4b7c-8708-d20330ed07d6",
            "no_tiket": "#421492",
            "review": "staff nya ramah"
        }
    ]
    
    print(f"📝 Testing with {len(test_records)} records...")
    
    try:
        # Test the analyze_sentiments method
        results, errors = await service.analyze_sentiments(test_records)
        
        print(f"\n✅ Analysis completed!")
        print(f"📊 Results: {len(results)} successful")
        print(f"❌ Errors: {len(errors)}")
        
        if results:
            print(f"\n🎯 Successful Results:")
            for i, result in enumerate(results, 1):
                print(f"  {i}. ID: {result.get('id')}")
                print(f"     Sentiment: {result.get('sentiment')}")
                print(f"     Score: {result.get('sentiment_score')}")
                print(f"     Reasons: {result.get('sentiment_reasons')}")
                print(f"     Themes: {result.get('sentiment_themes')}")
                print(f"     Suggestion: {result.get('sentiment_suggestion')}")
                print()
        
        if errors:
            print(f"\n⚠️  Errors:")
            for i, error in enumerate(errors, 1):
                print(f"  {i}. {error}")
        
        return len(results) > 0
        
    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_single_record():
    """Test single record analysis"""
    print("\n🔍 Testing single record analysis...")
    
    service = SentimentAnalysisService()
    
    test_record = {
        "id": "test-single-record",
        "no_tiket": "#TEST123",
        "review": "Pelayanan sangat memuaskan, staff ramah dan cepat"
    }
    
    try:
        result, error = await service.analyze_single_record(test_record)
        
        if result:
            print(f"✅ Single record analysis successful!")
            print(f"   Sentiment: {result.get('sentiment')}")
            print(f"   Score: {result.get('sentiment_score')}")
            return True
        elif error:
            print(f"❌ Single record analysis failed: {error}")
            return False
        else:
            print(f"❌ Single record analysis returned no result")
            return False
            
    except Exception as e:
        print(f"❌ Single record test failed: {str(e)}")
        return False

def test_request_formatting():
    """Test the request data formatting"""
    print("\n🔧 Testing request data formatting...")
    
    service = SentimentAnalysisService()
    
    test_records = [
        {
            "id": "test-1",
            "no_tiket": "#123",
            "review": "Test review"
        }
    ]
    
    try:
        request_data = service._format_request_data(test_records)
        print(f"✅ Request formatting successful!")
        print(f"📦 Formatted data: {request_data}")
        
        # Verify it's valid JSON
        import json
        parsed_question = json.loads(request_data['question'])
        print(f"✅ JSON parsing successful: {parsed_question}")
        return True
        
    except Exception as e:
        print(f"❌ Request formatting failed: {str(e)}")
        return False

async def main():
    """Run all tests"""
    print("🧪 SentimentAnalysisService Test Suite")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Request formatting
    total_tests += 1
    if test_request_formatting():
        tests_passed += 1
    
    # Test 2: Single record analysis
    total_tests += 1
    if await test_single_record():
        tests_passed += 1
    
    # Test 3: Batch analysis (same as Postman)
    total_tests += 1
    if await test_sentiment_analysis():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Sentiment analysis service is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check the logs above for details.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)