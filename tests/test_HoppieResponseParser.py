from hoppie_connector.Responses import ErrorResponse, SuccessResponse, HoppieResponseParser
import unittest

class TestHoppieResponseParser(unittest.TestCase):
    def test_error_response(self): self.assertIsInstance(HoppieResponseParser().parse('error {illegal logon code}'), ErrorResponse)
    def test_success_response(self): self.assertIsInstance(HoppieResponseParser().parse('ok'), SuccessResponse)