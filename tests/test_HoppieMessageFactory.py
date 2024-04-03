from hoppie_connector.Messages import PeekMessage, PollMessage, TelexMessage, ProgressMessage, PingMessage, AdscMessage, HoppieMessageFactory
from datetime import time, datetime, UTC
import unittest

class TestHoppieMessageFactory(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self._UUT = HoppieMessageFactory('OPS')

    def test_create_peek(self):     self.assertIsInstance(self._UUT.create_peek(), PeekMessage)
    def test_create_poll(self):     self.assertIsInstance(self._UUT.create_poll(), PollMessage)
    def test_create_telex(self):    self.assertIsInstance(self._UUT.create_telex('OPS', ''), TelexMessage)
    def test_create_ping(self):     self.assertIsInstance(self._UUT.create_ping(), PingMessage)
    def test_telex_from_data(self): 
        actual = self._UUT.create_from_data({'from': 'CALLSIGN', 'type': 'telex', 'packet': ''})
        self.assertIsInstance(actual, TelexMessage)
    def test_progress_from_data(self): 
        actual = self._UUT.create_from_data({'from': 'CALLSIGN', 'type': 'progress', 'packet': 'ZZZZ/ZZZZ OUT/0000'})
        self.assertIsInstance(actual, ProgressMessage)
    def test_adsc_from_data(self):
        actual = self._UUT.create_from_data({'from': 'CALLSIGN', 'type': 'ads-c', 'packet': 'REPORT CALLSIGN 011820 0.000000 0.000000 0'})
        self.assertIsInstance(actual, AdscMessage)

class TestHoppieMessageFactoryErrorHandling(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self._UUT = HoppieMessageFactory('OPS')

    def test_invalid_type(self):
        self.assertRaises(ValueError, lambda: self._UUT.create_from_data({'id': 0, 'from': 'CALLSIGN', 'type': 'invalid', 'packet': ''}))

    def test_unimplemented_type(self):
        self.assertRaises(ValueError, lambda: self._UUT.create_from_data({'id': 0, 'from': 'CALLSIGN', 'type': 'poll', 'packet': ''}))
        self.assertRaises(ValueError, lambda: self._UUT.create_from_data({'id': 0, 'from': 'CALLSIGN', 'type': 'peek', 'packet': ''}))

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
    _PRESET: dict = {'from': 'CALLSIGN', 'type': 'telex', 'packet': ''}

    def setUp(self) -> None:
        super().setUp()
        self._UUT = HoppieMessageFactory('OPS')

    def test_empty_message(self):
        actual: TelexMessage = self._UUT.create_from_data({**self._PRESET, 'packet': ''})
        self.assertEqual('', actual.get_message())

    def test_valid_message(self):
        actual: TelexMessage = self._UUT.create_from_data({**self._PRESET, 'packet': 'Message'})
        self.assertEqual('Message', actual.get_message())

    def test_oversize_content(self):
        self.assertRaises(ValueError, lambda: self._UUT.create_from_data({**self._PRESET, 'packet': 221*'a'}))

class TestProgressMessageFactoryCreate(unittest.TestCase):
    _EXPECTED_FROM: str = 'CALLSIGN'
    
    def setUp(self) -> None:
        super().setUp()
        self._UUT = HoppieMessageFactory(self._EXPECTED_FROM)

    def test_create_from(self):
        actual: ProgressMessage = self._UUT.create_progress('OPS', 'ZZZZ', 'ZZZZ', time_out=time(hour=0))
        self.assertEqual(self._EXPECTED_FROM, actual.get_from_name())

    def test_create_to(self):
        actual: ProgressMessage = self._UUT.create_progress('OPS', 'ZZZZ', 'ZZZZ', time_out=time(hour=0))
        self.assertEqual('OPS', actual.get_to_name())

    def test_create_time_out(self):
        actual: ProgressMessage = self._UUT.create_progress('OPS', 'ZZZZ', 'ZZZZ', time_out=time(hour=0))
        self.assertEqual(time(hour=0), actual.get_time_out())

    def test_create_time_off(self):
        actual: ProgressMessage = self._UUT.create_progress('OPS', 'ZZZZ', 'ZZZZ', time_out=time(hour=0), time_off=time(hour=1))
        self.assertEqual(time(hour=1), actual.get_time_off())

    def test_create_time_on(self):
        actual: ProgressMessage = self._UUT.create_progress('OPS', 'ZZZZ', 'ZZZZ', time_out=time(hour=0), time_off=time(hour=1), time_on=time(hour=2))
        self.assertEqual(time(hour=2), actual.get_time_on())

    def test_create_time_in(self):
        actual: ProgressMessage = self._UUT.create_progress('OPS', 'ZZZZ', 'ZZZZ', time_out=time(hour=0), time_off=time(hour=1), time_on=time(hour=2), time_in=time(hour=3))
        self.assertEqual(time(hour=3), actual.get_time_in())

    def test_create_eta(self):
        actual: ProgressMessage = self._UUT.create_progress('OPS', 'ZZZZ', 'ZZZZ', time_out=time(hour=0), time_eta=time(hour=1))
        self.assertEqual(time(hour=1), actual.get_eta())

class TestProgressMessageFactoryFromData(unittest.TestCase):
    _PRESET: dict = {'from': 'CALLSIGN', 'type': 'progress', 'packet': 'ZZZZ/ZZZZ OUT/0000'}

    def setUp(self) -> None:
        super().setUp()
        self._UUT = HoppieMessageFactory('OPS')

    def test_valid_departure(self):
        actual: ProgressMessage = self._UUT.create_from_data({**self._PRESET, 'packet': 'EDDF/ZZZZ OUT/0000'})
        self.assertEqual('EDDF', actual.get_departure())

    def test_valid_arrival(self):
        actual: ProgressMessage = self._UUT.create_from_data({**self._PRESET, 'packet': 'ZZZZ/EDDH OUT/0000'})
        self.assertEqual('EDDH', actual.get_arrival())

    def test_time_out(self):
        actual: ProgressMessage = self._UUT.create_from_data({**self._PRESET, 'packet': 'ZZZZ/ZZZZ OUT/1820'})
        expected = datetime.strptime('1820', '%H%M').replace(tzinfo=UTC).timetz()
        self.assertEqual(expected, actual.get_time_out())

    def test_time_out_eta(self):
        actual: ProgressMessage = self._UUT.create_from_data({**self._PRESET, 'packet': 'ZZZZ/ZZZZ OUT/0000 ETA/1820'})
        expected = datetime.strptime('1820', '%H%M').replace(tzinfo=UTC).timetz()
        self.assertEqual(expected, actual.get_eta())

    def test_time_off(self):
        actual: ProgressMessage = self._UUT.create_from_data({**self._PRESET, 'packet': 'ZZZZ/ZZZZ OUT/0000 OFF/1820'})
        expected = datetime.strptime('1820', '%H%M').replace(tzinfo=UTC).timetz()
        self.assertEqual(expected, actual.get_time_off())

    def test_time_off_eta(self):
        actual: ProgressMessage = self._UUT.create_from_data({**self._PRESET, 'packet': 'ZZZZ/ZZZZ OUT/0000 OFF/0001 ETA/1820'})
        expected = datetime.strptime('1820', '%H%M').replace(tzinfo=UTC).timetz()
        self.assertEqual(expected, actual.get_eta())

    def test_time_on(self):
        actual: ProgressMessage = self._UUT.create_from_data({**self._PRESET, 'packet': 'ZZZZ/ZZZZ OUT/0000 OFF/0001 ON/1820'})
        expected = datetime.strptime('1820', '%H%M').replace(tzinfo=UTC).timetz()
        self.assertEqual(expected, actual.get_time_on())

    def test_time_in(self):
        actual: ProgressMessage = self._UUT.create_from_data({**self._PRESET, 'packet': 'ZZZZ/ZZZZ OUT/0000 OFF/0001 ON/0002 IN/1820'})
        expected = datetime.strptime('1820', '%H%M').replace(tzinfo=UTC).timetz()
        self.assertEqual(expected, actual.get_time_in())

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
        actual: ProgressMessage = self._UUT.create_from_data({**self._PRESET, 'packet': 'ZZZZ/ZZZZ OUT/1820 OFF/----- ON/----- ETA/-----'})
        expected = datetime.strptime('1820', '%H%M').replace(tzinfo=UTC).timetz()
        self.assertEqual(expected, actual.get_time_out())
        self.assertIsNone(actual.get_time_off())
        self.assertIsNone(actual.get_time_on())
        self.assertIsNone(actual.get_eta())

class TestPingMessageFactoryCreate(unittest.TestCase):
    _EXPECTED_FROM: str = 'OPS'

    def setUp(self) -> None:
        super().setUp()
        self._UUT = HoppieMessageFactory(self._EXPECTED_FROM)

    def test_create_from(self):
        actual: PingMessage = self._UUT.create_ping()
        self.assertEqual(self._EXPECTED_FROM, actual.get_from_name())

    def test_create_to(self):
        actual: PingMessage = self._UUT.create_ping()
        self.assertEqual('SERVER', actual.get_to_name())

    def test_create_stations(self):
        actual: PingMessage = self._UUT.create_ping('CALLSIGN')
        self.assertEqual(['CALLSIGN'], actual.get_stations())

class TestAdscMessageFactoryFromData(unittest.TestCase):
    _PRESET: dict = {'from': 'CALLSIGN', 'type': 'ads-c', 'packet': 'REPORT CALLSIGN 011820 1.000000 2.000000 3'}

    def setUp(self) -> None:
        super().setUp()
        self._UUT = HoppieMessageFactory('OPS')
        
    def test_reptime(self):
        expected = datetime.strptime('011820', r'%d%H%M').replace(tzinfo=UTC)
        actual: AdscMessage = self._UUT.create_from_data({**self._PRESET})
        self.assertEqual(expected, actual.get_report_time())

    def test_position(self):
        expected = (1.0, 2.0)
        actual: AdscMessage = self._UUT.create_from_data({**self._PRESET})
        self.assertAlmostEqual(expected[0], actual.get_position()[0])
        self.assertAlmostEqual(expected[1], actual.get_position()[1])

    def test_altitude(self):
        expected = 3.0
        actual: AdscMessage = self._UUT.create_from_data({**self._PRESET})
        self.assertAlmostEqual(expected, actual.get_altitude())

    def test_heading(self):
        expected = 40.0
        actual: AdscMessage = self._UUT.create_from_data({**self._PRESET, 'packet': 'REPORT CALLSIGN 011820 1.000000 2.000000 3 40'})
        self.assertAlmostEqual(expected, actual.get_heading())

    def test_invalid_fltnum(self):
        self.assertRaises(ValueError, lambda: self._UUT.create_from_data({**self._PRESET, 'packet': 'REPORT INVALID 011820 1.000000 2.000000 3'}))

    def test_missing_fltnum(self):
        self.assertRaises(ValueError, lambda: self._UUT.create_from_data({**self._PRESET, 'packet': 'REPORT 011820 1.000000 2.000000 3'}))

class TestHoppieMessageFactoryComparison(unittest.TestCase):
    def test_same(self):
        value1 = HoppieMessageFactory('OPS')
        value2 = value1
        self.assertEqual(value1, value2)

    def test_equal_content(self):
        value1 = HoppieMessageFactory('OPS')
        value2 = HoppieMessageFactory('OPS')
        self.assertEqual(value1, value2)

    def test_differing(self):
        value1 = HoppieMessageFactory('OPS')
        value2 = HoppieMessageFactory('CALLSIGN')
        self.assertNotEqual(value1, value2)

class TestHoppieMessageFactoryRepresentation(unittest.TestCase):
    def test_repr(self):
        expected = HoppieMessageFactory('OPS')
        actual = eval(repr(expected))
        self.assertEqual(expected, actual)