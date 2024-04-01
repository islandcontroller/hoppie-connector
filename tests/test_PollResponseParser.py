from hoppie_connector.Responses import PollSuccessResponse, PollResponseParser
import unittest

class TestPollResponseParser(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self._UUT = PollResponseParser()

    def test_valid_item(self):
        expected = [{'from': 'FROM', 'type': 'type', 'packet': 'packet'}]
        actual: PollSuccessResponse = self._UUT.parse('ok {FROM type {packet}}')
        self.assertListEqual(expected, actual.get_data())

    def test_empty_packet(self):
        expected = [{'from': 'FROM', 'type': 'type', 'packet': ''}]
        actual: PollSuccessResponse = self._UUT.parse('ok {FROM type {}}')
        self.assertListEqual(expected, actual.get_data())

    def test_item_types(self):
        expected = [
            {'from': 'FROM', 'type': 'ads-c', 'packet': ''},
            {'from': 'FROM', 'type': 'progress', 'packet': ''},
            {'from': 'FROM', 'type': 'telex', 'packet': ''},
            {'from': 'FROM', 'type': 'datareq', 'packet': ''}
        ]
        actual: PollSuccessResponse = self._UUT.parse('ok {FROM ads-c {}} {FROM progress {}} {FROM telex {}} {FROM datareq {}}')
        self.assertListEqual(expected, actual.get_data())

    def test_multiple_items(self):
        expected = [
            {'from': 'FROM', 'type': 'type', 'packet': 'packet'},
            {'from': 'FROM', 'type': 'type', 'packet': 'packet'}
        ]
        actual: PollSuccessResponse = self._UUT.parse('ok {FROM type {packet}} {FROM type {packet}}')
        self.assertListEqual(expected, actual.get_data())

    def test_omit_malformed_items(self):
        expected = [
            {'from': 'FROM', 'type': 'type', 'packet': 'packet'},
            {'from': 'FROM', 'type': 'type', 'packet': 'packet'}
        ]
        actual: PollSuccessResponse = self._UUT.parse('ok {FROM type {packet}} {invalid} {FROM type {packet}}')
        self.assertListEqual(expected, actual.get_data())

    def test_space_in_type_name(self):
        expected = [{'from': 'FROM', 'type': 'type name', 'packet': ''}]
        actual: PollSuccessResponse = self._UUT.parse('ok {FROM type name {}}')
        self.assertListEqual(expected, actual.get_data())

class TestPollResponseParserComparison(unittest.TestCase):
    def test_same(self):
        value1 = PollResponseParser()
        value2 = value1
        self.assertEqual(value1, value2)

    def test_equal_type(self):
        value1 = PollResponseParser()
        value2 = PollResponseParser()
        self.assertEqual(value1, value2)
    
    def test_differing_type(self):
        value1 = PollResponseParser()
        value2 = None
        self.assertNotEqual(value1, value2)

class TestPollResponseParserRepresentation(unittest.TestCase):
    def test_repr(self):
        expected = PollResponseParser()
        actual = eval(repr(expected))
        self.assertEqual(expected, actual)
