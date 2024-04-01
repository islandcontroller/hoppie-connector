from hoppie_connector.Responses import PeekSuccessResponse, PeekResponseParser
import unittest

class TestPeekResponseParser(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self._UUT = PeekResponseParser()

    def test_empty_response(self):
        actual: PeekSuccessResponse = self._UUT.parse('ok')
        self.assertListEqual([], actual.get_data())

    def test_malformed_item(self):
        actual: PeekSuccessResponse = self._UUT.parse('ok {malformed item}')
        self.assertListEqual([], actual.get_data())

    def test_valid_item(self):
        expected = [{'id': 1, 'from': 'FROM', 'type': 'type', 'packet': 'packet'}]
        actual: PeekSuccessResponse = self._UUT.parse('ok {1 FROM type {packet}}')
        self.assertListEqual(expected, actual.get_data())

    def test_empty_packet(self):
        expected = [{'id': 1, 'from': 'FROM', 'type': 'type', 'packet': ''}]
        actual: PeekSuccessResponse = self._UUT.parse('ok {1 FROM type {}}')
        self.assertListEqual(expected, actual.get_data())

    def test_item_types(self):
        expected = [
            {'id': 1, 'from': 'FROM', 'type': 'ads-c', 'packet': ''},
            {'id': 2, 'from': 'FROM', 'type': 'progress', 'packet': ''},
            {'id': 3, 'from': 'FROM', 'type': 'telex', 'packet': ''},
            {'id': 4, 'from': 'FROM', 'type': 'datareq', 'packet': ''}
        ]
        actual: PeekSuccessResponse = self._UUT.parse('ok {1 FROM ads-c {}} {2 FROM progress {}} {3 FROM telex {}} {4 FROM datareq {}}')
        self.assertListEqual(expected, actual.get_data())

    def test_multiple_items(self):
        expected = [
            {'id': 1, 'from': 'FROM', 'type': 'type', 'packet': 'packet'},
            {'id': 2, 'from': 'FROM', 'type': 'type', 'packet': 'packet'}
        ]
        actual: PeekSuccessResponse = self._UUT.parse('ok {1 FROM type {packet}} {2 FROM type {packet}}')
        self.assertListEqual(expected, actual.get_data())

    def test_omit_malformed_items(self):
        expected = [
            {'id': 1, 'from': 'FROM', 'type': 'type', 'packet': 'packet'},
            {'id': 3, 'from': 'FROM', 'type': 'type', 'packet': 'packet'}
        ]
        actual: PeekSuccessResponse = self._UUT.parse('ok {1 FROM type {packet}} {invalid} {3 FROM type {packet}}')
        self.assertListEqual(expected, actual.get_data())

    def test_space_in_type_name(self):
        expected = [{'id': 1, 'from': 'FROM', 'type': 'type name', 'packet': ''}]
        actual: PeekSuccessResponse = self._UUT.parse('ok {1 FROM type name {}}')
        self.assertListEqual(expected, actual.get_data())

class TestPeekResponseParserComparison(unittest.TestCase):
    def test_same(self):
        value1 = PeekResponseParser()
        value2 = value1
        self.assertEqual(value1, value2)

    def test_equal_type(self):
        value1 = PeekResponseParser()
        value2 = PeekResponseParser()
        self.assertEqual(value1, value2)
    
    def test_differing_type(self):
        value1 = PeekResponseParser()
        value2 = None
        self.assertNotEqual(value1, value2)

class TestPeekResponseParserRepresentation(unittest.TestCase):
    def test_repr(self):
        expected = PeekResponseParser()
        actual = eval(repr(expected))
        self.assertEqual(expected, actual)
