from hoppie_connector.Responses import PingSuccessResponse, PingResponseParser
import unittest

class TestPingResponseParser(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self._UUT = PingResponseParser()

    def test_empty_response(self):
        actual: PingSuccessResponse = self._UUT.parse('ok')
        self.assertListEqual([], actual.get_stations())

    def test_single_station(self):
        expected = ['NAME1']
        actual: PingSuccessResponse = self._UUT.parse('ok {NAME1}')
        self.assertListEqual(expected, actual.get_stations())

    def test_omit_malformed(self):
        expected = ['NAME1', 'NAME3']
        actual: PingSuccessResponse = self._UUT.parse('ok {NAME1 invalid NAME3}')
        self.assertListEqual(expected, actual.get_stations())

class TestPingkResponseParserComparison(unittest.TestCase):
    def test_same(self):
        value1 = PingResponseParser()
        value2 = value1
        self.assertEqual(value1, value2)

    def test_equal_type(self):
        value1 = PingResponseParser()
        value2 = PingResponseParser()
        self.assertEqual(value1, value2)
    
    def test_differing_type(self):
        value1 = PingResponseParser()
        value2 = None
        self.assertNotEqual(value1, value2)

class TestPingResponseParserRepresentation(unittest.TestCase):
    def test_repr(self):
        expected = PingResponseParser()
        actual = eval(repr(expected))
        self.assertEqual(expected, actual)
