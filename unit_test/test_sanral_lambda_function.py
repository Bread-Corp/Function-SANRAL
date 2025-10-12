import unittest
import json
from unittest.mock import patch, Mock
import sys
import re
import os

# Patch boto3 before importing lambda_function
mock_boto3 = Mock()
mock_boto3.client.return_value = Mock()
sys.modules['boto3'] = mock_boto3

import lambda_function

class TestSanralLambdaFunction(unittest.TestCase):

    @patch('lambda_function.requests.get')
    @patch('lambda_function.sqs_client.send_message_batch')
    @patch('lambda_function.SanralTender.from_api_response')
    def test_lambda_handler_success(self, mock_from_api, mock_sqs, mock_get):
        # ✅ Load sample JSON from file
        with open(os.path.join('test_data', 'sample_sanral.json'), 'r') as f:
            sample_data = json.load(f)

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json = lambda: sample_data
        mock_get.return_value = mock_response

        mock_tender = Mock()
        mock_tender.to_dict.return_value = {"title": "Road Upgrade"}
        mock_from_api.return_value = mock_tender

        mock_sqs.return_value = {"Successful": [{"Id": "tender_message_0_0"}]}

        result = lambda_function.lambda_handler({}, {})
        self.assertEqual(result['statusCode'], 200)
        self.assertIn("Tender data processed", result['body'])

    @patch('lambda_function.requests.get')
    def test_lambda_handler_fetch_fail(self, mock_get):
        mock_get.side_effect = lambda_function.requests.exceptions.RequestException("Network error")
        result = lambda_function.lambda_handler({}, {})
        self.assertEqual(result['statusCode'], 502)
        self.assertIn("Failed to fetch data from source API", result['body'])

    def test_closing_date_regex(self):
        text = "Closing Date: 2025/12/31 14:00"
        match = re.search(r'Closing Date:\s*([\d/]+\s*[\d:]+)', text)
        self.assertEqual(match.group(1), "2025/12/31 14:00")

    @patch('lambda_function.requests.get')
    @patch('lambda_function.sqs_client.send_message_batch')
    @patch('lambda_function.SanralTender.from_api_response')
    def test_lambda_handler_with_malformed_row(self, mock_from_api, mock_sqs, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json = lambda: {
            'tenders': [None, ['valid', 'row', 'data', 'here', 'text', '2025/12/31 14:00']],
            'total_filtered': 2
        }
        mock_get.return_value = mock_response

        mock_tender = Mock()
        mock_tender.to_dict.return_value = {"title": "Valid Tender"}
        mock_from_api.side_effect = lambda row: None if row is None else mock_tender

        mock_sqs.return_value = {"Successful": [{"Id": "tender_message_0_0"}]}

        result = lambda_function.lambda_handler({}, {})
        self.assertEqual(result['statusCode'], 200)
        self.assertIn("Tender data processed", result['body'])

    @patch('lambda_function.requests.get')
    @patch('lambda_function.sqs_client.send_message_batch')
    @patch('lambda_function.SanralTender.from_api_response')
    def test_lambda_handler_with_sqs_failure(self, mock_from_api, mock_sqs, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json = lambda: {
            'tenders': [['<a href="/tender/123">RFP123/2025</a>', 'Construction', 'KZN', 'Desc', 'Text', '2025/12/31 14:00']],
            'total_filtered': 1
        }
        mock_get.return_value = mock_response

        mock_tender = Mock()
        mock_tender.to_dict.return_value = {"title": "Road Upgrade"}
        mock_from_api.return_value = mock_tender

        mock_sqs.return_value = {
            "Successful": [],
            "Failed": [{"Id": "tender_message_0_0", "Message": "AccessDenied"}]
        }

        result = lambda_function.lambda_handler({}, {})
        self.assertEqual(result['statusCode'], 200)
        self.assertIn("Tender data processed", result['body'])

if __name__ == '__main__':
    unittest.main()

