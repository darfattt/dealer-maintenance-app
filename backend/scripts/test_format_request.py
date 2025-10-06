"""
Test script to verify the _format_request_data output format
"""
import sys
import os

# Add the customer service to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend-microservices', 'services', 'customer'))

def test_format_request_data():
    """Test the format of request data"""
    from app.services.sentiment_analysis_service import SentimentAnalysisService

    # Mock settings for initialization
    class MockSettings:
        sentiment_api_url = "http://test.com"
        sentiment_api_token = "test_token"
        sentiment_api_timeout = 30
        sentiment_api_max_retries = 3
        sentiment_api_retry_delay = 2
        sentiment_api_connect_timeout = 10
        sentiment_api_read_timeout = 120
        sentiment_circuit_breaker_failure_threshold = 5
        sentiment_circuit_breaker_timeout = 300

    # Temporarily replace settings
    import app.config as config
    original_settings = config.settings
    config.settings = MockSettings()

    try:
        # Create service instance
        service = SentimentAnalysisService()

        # Test data
        test_records = [
            {
                'id': '5fbd7604-6475-4ebf-ba18-bada090bc129',
                'no_tiket': 'Ci9DQUlRQUNvZENodHljRjlvT2pZMVpHWkRka3gxVTJSdGFuTnFieko0YTBKa2NWRRAB',
                'review': 'Pelayanan mantapp respon cepatt, terimakasii\ud83d\ude4f\ud83c\udffb'
            }
        ]

        # Format the request
        result = service._format_request_data(test_records)

        print("=" * 80)
        print("TEST: Single Record Format")
        print("=" * 80)
        print(f"Result type: {type(result)}")
        print(f"Question key exists: {'question' in result}")
        print(f"\nFormatted request body:")
        print(result)
        print(f"\nQuestion value type: {type(result['question'])}")
        print(f"Question value (repr):\n{repr(result['question'])}")

        # Test with multiple records
        test_records_multi = [
            {
                'id': '5fbd7604-6475-4ebf-ba18-bada090bc129',
                'no_tiket': 'Ci9DQUlRQUNvZENodHljRjlvT2pZMVpHWkRka3gxVTJSdGFuTnFieko0YTBKa2NWRRAB',
                'review': 'Pelayanan mantapp respon cepatt, terimakasii\ud83d\ude4f\ud83c\udffb'
            },
            {
                'id': 'aca541f7-c630-4884-aa61-570b8f9ba83f',
                'no_tiket': 'Ci9DQUlRQUNvZENodHljRjlvT25OSFNYazFRamwzYVhCME4zVjJVa2RIT0hsaWFHYxAB',
                'review': 'Mantap \ud83d\udc4d'
            }
        ]

        result_multi = service._format_request_data(test_records_multi)

        print("\n" + "=" * 80)
        print("TEST: Multiple Records Format")
        print("=" * 80)
        print(f"\nFormatted request body:")
        print(result_multi)
        print(f"\nQuestion value (repr):\n{repr(result_multi['question'])}")

        # Test with single quote in review text
        test_records_quote = [
            {
                'id': 'test-id-123',
                'no_tiket': 'TICKET123',
                'review': "It's a great service!"
            }
        ]

        result_quote = service._format_request_data(test_records_quote)

        print("\n" + "=" * 80)
        print("TEST: Record with Single Quote in Review")
        print("=" * 80)
        print(f"\nFormatted request body:")
        print(result_quote)
        print(f"\nQuestion value (repr):\n{repr(result_quote['question'])}")

        print("\n" + "=" * 80)
        print("EXPECTED FORMAT:")
        print("=" * 80)
        expected = {
            "question": "[ { 'id': '5fbd7604-6475-4ebf-ba18-bada090bc129', 'no_tiket': 'Ci9DQUlRQUNvZENodHljRjlvT2pZMVpHWkRka3gxVTJSdGFuTnFieko0YTBKa2NWRRAB','review': 'Pelayanan mantapp respon cepatt, terimakasii\\ud83d\\ude4f\\ud83c\\udffb' }]"
        }
        print(expected)
        print(f"\nExpected question value (repr):\n{repr(expected['question'])}")

        print("\n" + "=" * 80)
        print("FORMAT COMPARISON:")
        print("=" * 80)
        has_single_quotes = "'id':" in result['question']
        has_space_after = result['question'].startswith('[ ')
        has_space_before = result['question'].endswith(' ]')
        has_curly_braces = '{' in result['question']
        print(f"Uses single quotes for keys: {has_single_quotes}")
        print(f"Has space after opening bracket: {has_space_after}")
        print(f"Has space before closing bracket: {has_space_before}")
        print(f"Uses curly braces for objects: {has_curly_braces}")

    finally:
        # Restore original settings
        config.settings = original_settings

if __name__ == "__main__":
    test_format_request_data()