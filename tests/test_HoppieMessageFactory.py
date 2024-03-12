from hoppie_connector.Messages import PeekMessage, PollMessage, TelexMessage, ProgressMessage, HoppieMessageFactory
from hoppie_connector.Responses import HoppieResponseParser
from datetime import datetime, UTC
import unittest

class TestHoppieMessageFactory(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self._UUT = HoppieMessageFactory('OPS')

    def test_create_peek(self):     self.assertIsInstance(self._UUT.create_peek(), PeekMessage)
    def test_create_poll(self):     self.assertIsInstance(self._UUT.create_poll(), PollMessage)
    def test_create_telex(self):    self.assertIsInstance(self._UUT.create_telex('OPS', ''), TelexMessage)
    def test_telex_from_data(self): 
        actual = self._UUT.create_from_data({'id': 0, 'from': 'CALLSIGN', 'type': 'telex', 'packet': ''})
        self.assertIsInstance(actual, tuple)
        self.assertIsInstance(actual[0], int)
        self.assertIsInstance(actual[1], TelexMessage)
    def test_progress_from_data(self): 
        actual = self._UUT.create_from_data({'id': 0, 'from': 'CALLSIGN', 'type': 'progress', 'packet': 'ZZZZ/ZZZZ OUT/0000'})
        self.assertIsInstance(actual, tuple)
        self.assertIsInstance(actual[0], int)
        self.assertIsInstance(actual[1], ProgressMessage)

class TestTelexMessageFactoryCreate(unittest.TestCase):
    _EXPECTED_FROM: str = 'CALLSIGN'

    def setUp(self) -> None:
        super().setUp()
        self._UUT = HoppieMessageFactory(self._EXPECTED_FROM)

    def test_create_from(self):
        actual: TelexMessage = self._UUT.create_telex('OPS', '')
        self.assertEqual(self._EXPECTED_FROM, actual.get_from_name())

    def test_create_to(self):
        actual: TelexMessage = self._UUT.create_telex('OPS', '')
        self.assertEqual('OPS', actual.get_to_name())

    def test_create_message(self):
        actual: TelexMessage = self._UUT.create_telex('OPS', 'Message')
        self.assertEqual('Message', actual.get_message())

class TestTelexMessageFactoryFromData(unittest.TestCase):
    _PRESET: dict = {'id': 0, 'from': 'CALLSIGN', 'type': 'telex', 'packet': ''}

    def setUp(self) -> None:
        super().setUp()
        self._UUT = HoppieMessageFactory('OPS')

    def test_message_id(self):
        actual: tuple[int, TelexMessage] = self._UUT.create_from_data({**self._PRESET, 'id': 1234})
        self.assertEqual(1234, actual[0])

    def test_empty_message(self):
        actual: tuple[int, TelexMessage] = self._UUT.create_from_data({**self._PRESET, 'packet': ''})
        self.assertEqual('', actual[1].get_message())

    def test_valid_message(self):
        actual: tuple[int, TelexMessage] = self._UUT.create_from_data({**self._PRESET, 'packet': 'Message'})
        self.assertEqual('Message', actual[1].get_message())

    def test_oversize_content(self):
        self.assertRaises(ValueError, lambda: self._UUT.create_from_data({**self._PRESET, 'packet': 221*'a'}))

class TestProgressMessageFactoryFromData(unittest.TestCase):
    _PRESET: dict = {'id': 0, 'from': 'CALLSIGN', 'type': 'progress', 'packet': 'ZZZZ/ZZZZ OUT/0000'}

    def setUp(self) -> None:
        super().setUp()
        self._UUT = HoppieMessageFactory('OPS')

    def test_message_id(self):
        actual: tuple[int, ProgressMessage] = self._UUT.create_from_data({**self._PRESET, 'id': 1234})
        self.assertEqual(1234, actual[0])

    def test_valid_departure(self):
        actual: tuple[int, ProgressMessage] = self._UUT.create_from_data({**self._PRESET, 'packet': 'EDDF/ZZZZ OUT/0000'})
        self.assertEqual('EDDF', actual[1].get_departure())

    def test_valid_arrival(self):
        actual: tuple[int, ProgressMessage] = self._UUT.create_from_data({**self._PRESET, 'packet': 'ZZZZ/EDDH OUT/0000'})
        self.assertEqual('EDDH', actual[1].get_arrival())

    def test_time_out(self):
        actual: tuple[int, ProgressMessage] = self._UUT.create_from_data({**self._PRESET, 'packet': 'ZZZZ/ZZZZ OUT/1820'})
        expected = datetime.strptime('1820', '%H%M').replace(tzinfo=UTC).timetz()
        self.assertEqual(expected, actual[1].get_time_out())

    def test_time_out_eta(self):
        actual: tuple[int, ProgressMessage] = self._UUT.create_from_data({**self._PRESET, 'packet': 'ZZZZ/ZZZZ OUT/0000 ETA/1820'})
        expected = datetime.strptime('1820', '%H%M').replace(tzinfo=UTC).timetz()
        self.assertEqual(expected, actual[1].get_eta())

    def test_time_off(self):
        actual: tuple[int, ProgressMessage] = self._UUT.create_from_data({**self._PRESET, 'packet': 'ZZZZ/ZZZZ OUT/0000 OFF/1820'})
        expected = datetime.strptime('1820', '%H%M').replace(tzinfo=UTC).timetz()
        self.assertEqual(expected, actual[1].get_time_off())

    def test_time_off_eta(self):
        actual: tuple[int, ProgressMessage] = self._UUT.create_from_data({**self._PRESET, 'packet': 'ZZZZ/ZZZZ OUT/0000 OFF/0001 ETA/1820'})
        expected = datetime.strptime('1820', '%H%M').replace(tzinfo=UTC).timetz()
        self.assertEqual(expected, actual[1].get_eta())

    def test_time_on(self):
        actual: tuple[int, ProgressMessage] = self._UUT.create_from_data({**self._PRESET, 'packet': 'ZZZZ/ZZZZ OUT/0000 OFF/0001 ON/1820'})
        expected = datetime.strptime('1820', '%H%M').replace(tzinfo=UTC).timetz()
        self.assertEqual(expected, actual[1].get_time_on())

    def test_time_in(self):
        actual: tuple[int, ProgressMessage] = self._UUT.create_from_data({**self._PRESET, 'packet': 'ZZZZ/ZZZZ OUT/0000 OFF/0001 ON/0002 IN/1820'})
        expected = datetime.strptime('1820', '%H%M').replace(tzinfo=UTC).timetz()
        self.assertEqual(expected, actual[1].get_time_in())

    def test_missing_out(self):
        self.assertRaises(ValueError, lambda: self._UUT.create_from_data({**self._PRESET, 'packet': 'ZZZZ/ZZZZ'}))

    def test_invalid_aprt(self):
        self.assertRaises(ValueError, lambda: self._UUT.create_from_data({**self._PRESET, 'packet': 'ZZZZ/EH01'}))

    def test_invalid_out(self):
        self.assertRaises(ValueError, lambda: self._UUT.create_from_data({**self._PRESET, 'packet': 'ZZZZ/ZZZZ OUT/9999'}))

    def test_invalid_off(self):
        self.assertRaises(ValueError, lambda: self._UUT.create_from_data({**self._PRESET, 'packet': 'ZZZZ/ZZZZ OUT/0000 OFF/9999'}))

    def test_invalid_on(self):
        self.assertRaises(ValueError, lambda: self._UUT.create_from_data({**self._PRESET, 'packet': 'ZZZZ/ZZZZ OUT/0000 OFF/0001 ON/9999'}))

    def test_special_empty_case(self):
        actual: tuple[int, ProgressMessage] = self._UUT.create_from_data({**self._PRESET, 'packet': 'ZZZZ/ZZZZ OUT/1820 OFF/----- ON/----- ETA/-----'})
        expected = datetime.strptime('1820', '%H%M').replace(tzinfo=UTC).timetz()
        self.assertEqual(expected, actual[1].get_time_out())
        self.assertIsNone(actual[1].get_time_off())
        self.assertIsNone(actual[1].get_time_on())
        self.assertIsNone(actual[1].get_eta())