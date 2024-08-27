from hoppie_connector.Messages import TelexMessage, ProgressMessage, AdscPeriodicReportMessage, CpdlcMessage, HoppieMessageParser
from datetime import datetime, UTC
import unittest

class TestHoppieMessageParser(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self._UUT = HoppieMessageParser('OPS')

    def test_parse_telex(self): 
        actual = self._UUT.parse({'from': 'CALLSIGN', 'type': 'telex', 'packet': ''})
        self.assertIsInstance(actual, TelexMessage)
    def test_parse_progress(self): 
        actual = self._UUT.parse({'from': 'CALLSIGN', 'type': 'progress', 'packet': 'ZZZZ/ZZZZ OUT/0000'})
        self.assertIsInstance(actual, ProgressMessage)
    def test_parse_adsc(self):
        actual = self._UUT.parse({'from': 'CALLSIGN', 'type': 'ads-c', 'packet': 'REPORT CALLSIGN 011820 0.000000 0.000000 0'})
        self.assertIsInstance(actual, AdscPeriodicReportMessage)
    def test_parse_cpdlc(self):
        actual = self._UUT.parse({'from': 'CALLSIGN', 'type': 'cpdlc', 'packet': '/data2/1/2/N/WILCO'})
        self.assertIsInstance(actual, CpdlcMessage)

class TestHoppieMessageParserErrorHandling(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self._UUT = HoppieMessageParser('OPS')

    def test_invalid_type(self):
        self.assertRaises(ValueError, lambda: self._UUT.parse({'id': 0, 'from': 'CALLSIGN', 'type': 'invalid', 'packet': ''}))

    def test_unimplemented_type(self):
        self.assertRaises(ValueError, lambda: self._UUT.parse({'id': 0, 'from': 'CALLSIGN', 'type': 'poll', 'packet': ''}))
        self.assertRaises(ValueError, lambda: self._UUT.parse({'id': 0, 'from': 'CALLSIGN', 'type': 'peek', 'packet': ''}))

class TestHoppieMessageParserComparison(unittest.TestCase):
    def test_same(self):
        value1 = HoppieMessageParser('OPS')
        value2 = value1
        self.assertEqual(value1, value2)

    def test_equal_content(self):
        value1 = HoppieMessageParser('OPS')
        value2 = HoppieMessageParser('OPS')
        self.assertEqual(value1, value2)

    def test_differing(self):
        value1 = HoppieMessageParser('OPS')
        value2 = HoppieMessageParser('CALLSIGN')
        self.assertNotEqual(value1, value2)

class TestHoppieMessageParserRepresentation(unittest.TestCase):
    def test_repr(self):
        expected = HoppieMessageParser('OPS')
        actual = eval(repr(expected))
        self.assertEqual(expected, actual)