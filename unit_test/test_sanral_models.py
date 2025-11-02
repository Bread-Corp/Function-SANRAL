import unittest
from unittest.mock import patch, Mock
from models import SanralTender, SupportingDoc
from datetime import datetime

class TestSupportingDoc(unittest.TestCase):
    def test_to_dict(self):
        # Test that SupportingDoc correctly serializes to a dictionary.
        doc = SupportingDoc(name="Tender PDF", url="https://example.com/tender.pdf")
        self.assertEqual(doc.to_dict(), {"name": "Tender PDF", "url": "https://example.com/tender.pdf"})

class TestSanralTender(unittest.TestCase):
    @patch('models.requests.get')
    def test_from_api_response_success(self, mock_get):
        # Test that SanralTender.from_api_response correctly parses valid input and detail page.
        mock_html = '''
            <html>
                <div class="page-header"><h2>Road Upgrade Tender</h2></div>
                <h3>Upgrade of N2 Section</h3>
                <table>
                    <tr><td>Tender Notice:</td><td>Full tender details including contact info: info@sanral.co.za</td></tr>
                    <tr><th>Create Date</th><td>October 10, 2025</td></tr>
                </table>
            </html>
        '''
        mock_get.return_value = Mock(status_code=200, text=mock_html)

        response_item = [
            '<a href="/tender/123">RFP123/2025</a>',
            'Construction',
            'KwaZulu-Natal',
            'Tender Notice: Upgrade of N2',
            'Full tender details including contact info: info@sanral.co.za',
            '2025/12/31 14:00'
        ]

        tender = SanralTender.from_api_response(response_item)
        self.assertIsNotNone(tender)
        self.assertEqual(tender.tender_number, "RFP123/2025")
        self.assertEqual(tender.category, "Construction")
        self.assertEqual(tender.region, "Kwazulu-Natal")
        self.assertEqual(tender.email, "info@sanral.co.za")
        self.assertEqual(tender.closing_date, datetime(2025, 12, 31, 14, 0))
        self.assertEqual(tender.published_date, datetime(2025, 10, 10))
        self.assertEqual(len(tender.supporting_docs), 1)

    def test_from_api_response_invalid_input(self):
        # Test that from_api_response returns None for malformed input.
        invalid_input = ["Only one item"]
        tender = SanralTender.from_api_response(invalid_input)
        self.assertIsNone(tender)

    def test_to_dict_structure(self):
        # Test that SanralTender.to_dict serializes all fields correctly.
        tender = SanralTender(
            title="Road Upgrade",
            description="Upgrade of N2",
            source="SANRAL",
            published_date=datetime(2025, 10, 10),
            closing_date=datetime(2025, 12, 31, 14, 0),
            supporting_docs=[SupportingDoc("Tender Details", "https://example.com")],
            tags=["infrastructure"],
            tender_number="RFP123/2025",
            category="Construction",
            region="KwaZulu-Natal",
            email="info@sanral.co.za",
            full_notice_text="Full tender details"
        )
        data = tender.to_dict()
        self.assertEqual(data["tenderNumber"], "RFP123/2025")
        self.assertEqual(data["category"], "Construction")
        self.assertEqual(data["region"], "KwaZulu-Natal")
        self.assertEqual(data["email"], "info@sanral.co.za")
        self.assertEqual(data["supporting_docs"][0]["name"], "Tender Details")
