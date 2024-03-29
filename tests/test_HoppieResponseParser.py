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

class TestErrorResponseParser(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self._UUT = HoppieResponseParser()

    def test_get_code(self):
        actual: ErrorResponse = self._UUT.parse('error {}')
        self.assertEqual(HoppieResponse.ResponseCode.ERROR, actual.get_code())

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

class TestSuccessResponseParser(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self._UUT = HoppieResponseParser()
    
    def test_internal_regex_mismatch(self):
        self.assertIsNone(self._UUT._parse_message_data_item(''))

class TestSuccessPeekResponseParser(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self._UUT = HoppieResponseParser()

    def test_get_code(self):
        actual: SuccessResponse = self._UUT.parse('ok')
        self.assertEqual(HoppieResponse.ResponseCode.OK, actual.get_code())

    def test_empty_response(self):
        actual: SuccessResponse = self._UUT.parse('ok')
        self.assertListEqual([], actual.get_items())

    def test_malformed_item(self):
        actual: SuccessResponse = self._UUT.parse('ok {malformed item}')
        self.assertListEqual([], actual.get_items())

    def test_valid_item(self):
        expected = [{'id': 1, 'from': 'FROM', 'type': 'type', 'packet': 'packet'}]
        actual: SuccessResponse = self._UUT.parse('ok {1 FROM type {packet}}')
        self.assertListEqual(expected, actual.get_items())

    def test_empty_packet(self):
        expected = [{'id': 1, 'from': 'FROM', 'type': 'type', 'packet': ''}]
        actual: SuccessResponse = self._UUT.parse('ok {1 FROM type {}}')
        self.assertListEqual(expected, actual.get_items())

    def test_item_types(self):
        expected = [
            {'id': 1, 'from': 'FROM', 'type': 'ads-c', 'packet': ''},
            {'id': 2, 'from': 'FROM', 'type': 'progress', 'packet': ''},
            {'id': 3, 'from': 'FROM', 'type': 'telex', 'packet': ''},
            {'id': 4, 'from': 'FROM', 'type': 'datareq', 'packet': ''}
        ]
        actual: SuccessResponse = self._UUT.parse('ok {1 FROM ads-c {}} {2 FROM progress {}} {3 FROM telex {}} {4 FROM datareq {}}')
        self.assertListEqual(expected, actual.get_items())

    def test_multiple_items(self):
        expected = [
            {'id': 1, 'from': 'FROM', 'type': 'type', 'packet': 'packet'},
            {'id': 2, 'from': 'FROM', 'type': 'type', 'packet': 'packet'}
        ]
        actual: SuccessResponse = self._UUT.parse('ok {1 FROM type {packet}} {2 FROM type {packet}}')
        self.assertListEqual(expected, actual.get_items())

    def test_omit_malformed_items(self):
        expected = [
            {'id': 1, 'from': 'FROM', 'type': 'type', 'packet': 'packet'},
            {'id': 3, 'from': 'FROM', 'type': 'type', 'packet': 'packet'}
        ]
        actual: SuccessResponse = self._UUT.parse('ok {1 FROM type {packet}} {invalid} {3 FROM type {packet}}')
        self.assertListEqual(expected, actual.get_items())

    def test_space_in_type_name(self):
        expected = [{'id': 1, 'from': 'FROM', 'type': 'type name', 'packet': ''}]
        actual: SuccessResponse = self._UUT.parse('ok {1 FROM type name {}}')
        self.assertListEqual(expected, actual.get_items())

class TestSuccessPollResponseParser(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self._UUT = HoppieResponseParser()

    def test_valid_item(self):
        expected = [{'id': None, 'from': 'FROM', 'type': 'type', 'packet': 'packet'}]
        actual: SuccessResponse = self._UUT.parse('ok {FROM type {packet}}')
        self.assertListEqual(expected, actual.get_items())

    def test_empty_packet(self):
        expected = [{'id': None, 'from': 'FROM', 'type': 'type', 'packet': ''}]
        actual: SuccessResponse = self._UUT.parse('ok {FROM type {}}')
        self.assertListEqual(expected, actual.get_items())

    def test_item_types(self):
        expected = [
            {'id': None, 'from': 'FROM', 'type': 'ads-c', 'packet': ''},
            {'id': None, 'from': 'FROM', 'type': 'progress', 'packet': ''},
            {'id': None, 'from': 'FROM', 'type': 'telex', 'packet': ''},
            {'id': None, 'from': 'FROM', 'type': 'datareq', 'packet': ''}
        ]
        actual: SuccessResponse = self._UUT.parse('ok {FROM ads-c {}} {FROM progress {}} {FROM telex {}} {FROM datareq {}}')
        self.assertListEqual(expected, actual.get_items())

    def test_multiple_items(self):
        expected = [
            {'id': None, 'from': 'FROM', 'type': 'type', 'packet': 'packet'},
            {'id': None, 'from': 'FROM', 'type': 'type', 'packet': 'packet'}
        ]
        actual: SuccessResponse = self._UUT.parse('ok {FROM type {packet}} {FROM type {packet}}')
        self.assertListEqual(expected, actual.get_items())

    def test_omit_malformed_items(self):
        expected = [
            {'id': None, 'from': 'FROM', 'type': 'type', 'packet': 'packet'},
            {'id': None, 'from': 'FROM', 'type': 'type', 'packet': 'packet'}
        ]
        actual: SuccessResponse = self._UUT.parse('ok {FROM type {packet}} {invalid} {FROM type {packet}}')
        self.assertListEqual(expected, actual.get_items())

    def test_space_in_type_name(self):
        expected = [{'id': None, 'from': 'FROM', 'type': 'type name', 'packet': ''}]
        actual: SuccessResponse = self._UUT.parse('ok {FROM type name {}}')
        self.assertListEqual(expected, actual.get_items())

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