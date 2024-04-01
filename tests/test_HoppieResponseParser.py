from hoppie_connector.Responses import HoppieResponse, ErrorResponse, SuccessResponse, HoppieResponseParser
import unittest

class TestHoppieResponseParser(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self._UUT = HoppieResponseParser()

    def test_error_response(self):   self.assertIsInstance(self._UUT.parse('error {}'), ErrorResponse)
    def test_success_response(self): self.assertIsInstance(self._UUT.parse('ok'), SuccessResponse)
    def test_invalid_response(self): self.assertRaises(ValueError, lambda: self._UUT.parse('invalid'))
    def test_empty_response(self):   self.assertRaises(ValueError, lambda: self._UUT.parse(''))

class TestHoppieResponseParserError(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self._UUT = HoppieResponseParser()

    def test_empty_reason(self):
        actual: ErrorResponse = self._UUT.parse('error {}')
        self.assertEqual('', actual.get_reason())

    def test_valid_reason(self):
        actual: ErrorResponse = self._UUT.parse('error {illegal logon code}')
        self.assertEqual('illegal logon code', actual.get_reason())

    def test_reason_containing_newline(self):
        actual: ErrorResponse = self._UUT.parse('error {message con-\ntaining newline}')
        self.assertEqual('message con-\ntaining newline', actual.get_reason())

    def test_malformed_response(self): 
        self.assertRaises(ValueError, lambda: self._UUT.parse('error malformed response'))

    def test_leading_garbage(self):
        actual: ErrorResponse = self._UUT.parse('error garbage {reason}')
        self.assertEqual('reason', actual.get_reason())

    def test_trailing_garbage(self):
        actual: ErrorResponse = self._UUT.parse('error {reason} garbage')
        self.assertEqual('reason', actual.get_reason())

class TestHoppieResponseParserComparison(unittest.TestCase):
    def test_same(self):
        value1 = HoppieResponseParser()
        value2 = value1
        self.assertEqual(value1, value2)

    def test_equal_type(self):
        value1 = HoppieResponseParser()
        value2 = HoppieResponseParser()
        self.assertEqual(value1, value2)
    
    def test_differing_type(self):
        value1 = HoppieResponseParser()
        value2 = None
        self.assertNotEqual(value1, value2)

class TestHoppieResponseParserRepresentation(unittest.TestCase):
    def test_repr(self):
        expected = HoppieResponseParser()
        actual = eval(repr(expected))
        self.assertEqual(expected, actual)
