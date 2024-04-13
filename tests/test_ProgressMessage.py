from hoppie_connector.Messages import ProgressMessage, HoppieMessage, HoppieMessage as Super
from datetime import datetime, time, timedelta, timezone, UTC
import unittest

class TestValidProgressMessage(unittest.TestCase):
    _EXPECTED_TYPE: HoppieMessage.MessageType = HoppieMessage.MessageType.PROGRESS
    _EXPECTED_DEP: str = 'EDDF'
    _EXPECTED_ARR: str = 'EDDH'
    _EXPECTED_OUT: time = time(hour=18, minute=20, tzinfo=UTC)
    _EXPECTED_PACKET: str = 'EDDF/EDDH OUT/1820'

    def setUp(self) -> None:
        super().setUp()
        self._UUT = ProgressMessage('CALLSIGN', 'OPS', self._EXPECTED_DEP, self._EXPECTED_ARR, self._EXPECTED_OUT)

    def test_get_msg_type(self):       self.assertEqual(self._EXPECTED_TYPE, self._UUT.get_msg_type())
    def test_get_departure(self):      self.assertEqual(self._EXPECTED_DEP, self._UUT.get_departure())
    def test_get_arrival(self):        self.assertEqual(self._EXPECTED_ARR, self._UUT.get_arrival())
    def test_get_time_out(self):       self.assertEqual(self._EXPECTED_OUT, self._UUT.get_time_out())
    def test_get_time_off(self):       self.assertIsNone(self._UUT.get_time_off())
    def test_get_time_on(self):        self.assertIsNone(self._UUT.get_time_on())
    def test_get_time_in(self):        self.assertIsNone(self._UUT.get_time_in())
    def test_get_eta(self):            self.assertIsNone(self._UUT.get_eta())
    def test_get_packet_content(self): self.assertEqual(self._EXPECTED_PACKET, self._UUT.get_packet_content())
    def test_hierarchy_super(self):    self.assertIsInstance(self._UUT, Super)

class TestValidProgressMessageTimezone(unittest.TestCase):
    _TIMEZONE = timezone = timezone(timedelta(hours=1))
    _EXPECTED_OUT: time = time(hour=18, minute=20, tzinfo=_TIMEZONE)
    _EXPECTED_PACKET: str = 'EDDF/EDDH OUT/1720'

    def setUp(self) -> None:
        super().setUp()
        self._UUT = ProgressMessage('CALLSIGN', 'OPS', 'EDDF', 'EDDH', self._EXPECTED_OUT)

    def test_get_time_out(self):       self.assertEqual(self._EXPECTED_OUT, self._UUT.get_time_out())
    def test_get_packet_content(self): self.assertEqual(self._EXPECTED_PACKET, self._UUT.get_packet_content())

class TestValidProgressMessageNoTimezone(unittest.TestCase):
    _EXPECTED_OUT: time = time(hour=18, minute=20, tzinfo=None)
    _EXPECTED_PACKET: str = 'EDDF/EDDH OUT/1820'

    def setUp(self) -> None:
        super().setUp()
        self._UUT = ProgressMessage('CALLSIGN', 'OPS', 'EDDF', 'EDDH', self._EXPECTED_OUT)

    def test_get_time_out(self):       self.assertEqual(self._EXPECTED_OUT, self._UUT.get_time_out())
    def test_get_packet_content(self): self.assertEqual(self._EXPECTED_PACKET, self._UUT.get_packet_content())

class TestValidProgressMessageEta(unittest.TestCase):
    _EXPECTED_OUT: time = time(hour=18, minute=20, tzinfo=UTC)
    _EXPECTED_ETA: time = time(hour=18, minute=25, tzinfo=UTC)
    _EXPECTED_PACKET: str = 'EDDF/EDDH OUT/1820 ETA/1825'

    def setUp(self) -> None:
        super().setUp()
        self._UUT = ProgressMessage('CALLSIGN', 'OPS', 'EDDF', 'EDDH', self._EXPECTED_OUT, self._EXPECTED_ETA)

    def test_get_eta(self):            self.assertEqual(self._EXPECTED_ETA, self._UUT.get_eta())
    def test_get_packet_content(self): self.assertEqual(self._EXPECTED_PACKET, self._UUT.get_packet_content())

class TestValidProgressMessageOff(unittest.TestCase):
    _EXPECTED_OUT: time = time(hour=18, minute=20, tzinfo=UTC)
    _EXPECTED_OFF: time = time(hour=18, minute=25, tzinfo=UTC)
    _EXPECTED_PACKET: str = 'EDDF/EDDH OUT/1820 OFF/1825'

    def setUp(self) -> None:
        super().setUp()
        self._UUT = ProgressMessage('CALLSIGN', 'OPS', 'EDDF', 'EDDH', self._EXPECTED_OUT, time_off=self._EXPECTED_OFF)

    def test_get_time_off(self):       self.assertEqual(self._EXPECTED_OFF, self._UUT.get_time_off())
    def test_get_packet_content(self): self.assertEqual(self._EXPECTED_PACKET, self._UUT.get_packet_content())

class TestValidProgressMessageOffEta(unittest.TestCase):
    _EXPECTED_OUT: time = time(hour=18, minute=20, second=0, tzinfo=UTC)
    _EXPECTED_OFF: time = time(hour=18, minute=25, tzinfo=UTC)
    _EXPECTED_ETA: time = time(hour=18, minute=30, tzinfo=UTC)
    _EXPECTED_PACKET: str = 'EDDF/EDDH OUT/1820 OFF/1825 ETA/1830'

    def setUp(self) -> None:
        super().setUp()
        self._UUT = ProgressMessage('CALLSIGN', 'OPS', 'EDDF', 'EDDH', self._EXPECTED_OUT, self._EXPECTED_ETA, self._EXPECTED_OFF)

    def test_get_packet_content(self): self.assertEqual(self._EXPECTED_PACKET, self._UUT.get_packet_content())

class TestValidProgressMessageOn(unittest.TestCase):
    _EXPECTED_OUT: time = time(hour=18, minute=20, second=0, tzinfo=UTC)
    _EXPECTED_OFF: time = time(hour=18, minute=25, tzinfo=UTC)
    _EXPECTED_ON: time = time(hour=18, minute=30, tzinfo=UTC)
    _EXPECTED_PACKET: str = 'EDDF/EDDH OUT/1820 OFF/1825 ON/1830'

    def setUp(self) -> None:
        super().setUp()
        self._UUT = ProgressMessage('CALLSIGN', 'OPS', 'EDDF', 'EDDH', self._EXPECTED_OUT, time_off=self._EXPECTED_OFF, time_on=self._EXPECTED_ON)

    def test_get_packet_content(self): self.assertEqual(self._EXPECTED_PACKET, self._UUT.get_packet_content())

class TestValidProgressMessageOnEta(unittest.TestCase):
    _EXPECTED_OUT: time = time(hour=18, minute=20, second=0, tzinfo=UTC)
    _EXPECTED_OFF: time = time(hour=18, minute=25, tzinfo=UTC)
    _EXPECTED_ON: time = time(hour=18, minute=30, tzinfo=UTC)
    _EXPECTED_ETA: time = time(hour=18, minute=35, tzinfo=UTC)
    _EXPECTED_PACKET: str = 'EDDF/EDDH OUT/1820 OFF/1825 ON/1830 ETA/1835'

    def setUp(self) -> None:
        super().setUp()
        self._UUT = ProgressMessage('CALLSIGN', 'OPS', 'EDDF', 'EDDH', self._EXPECTED_OUT, self._EXPECTED_ETA, self._EXPECTED_OFF, self._EXPECTED_ON)

    def test_get_packet_content(self): self.assertEqual(self._EXPECTED_PACKET, self._UUT.get_packet_content())

class TestValidProgressMessageIn(unittest.TestCase):
    _EXPECTED_OUT: time = time(hour=18, minute=20, second=0, tzinfo=UTC)
    _EXPECTED_OFF: time = time(hour=18, minute=25, tzinfo=UTC)
    _EXPECTED_ON: time = time(hour=18, minute=30, tzinfo=UTC)
    _EXPECTED_IN: time = time(hour=18, minute=35, tzinfo=UTC)
    _EXPECTED_PACKET: str = 'EDDF/EDDH OUT/1820 OFF/1825 ON/1830 IN/1835'

    def setUp(self) -> None:
        super().setUp()
        self._UUT = ProgressMessage('CALLSIGN', 'OPS', 'EDDF', 'EDDH', self._EXPECTED_OUT, time_off=self._EXPECTED_OFF, time_on=self._EXPECTED_ON, time_in=self._EXPECTED_IN)

    def test_get_packet_content(self): self.assertEqual(self._EXPECTED_PACKET, self._UUT.get_packet_content())

class TestProgressMessageInputValidation(unittest.TestCase):
    _TIME_1: time = time(hour=18, minute=20, second=0, tzinfo=UTC)
    _TIME_2: time = time(hour=18, minute=25, second=0, tzinfo=UTC)
    _TIME_3: time = time(hour=18, minute=30, second=0, tzinfo=UTC)
    _TIME_4: time = time(hour=18, minute=35, second=0, tzinfo=UTC)
    _TIME_5: time = time(hour=18, minute=40, second=0, tzinfo=UTC)

    def test_invalid_dep_code(self):   self.assertRaises(ValueError, lambda: ProgressMessage('CALLSIGN', 'OPS', 'EH02', 'EDDH', self._TIME_1))
    def test_invalid_arr_code(self):   self.assertRaises(ValueError, lambda: ProgressMessage('CALLSIGN', 'OPS', 'EDDF', 'abc',  self._TIME_1))
    def test_missing_out(self):        self.assertRaises(ValueError, lambda: ProgressMessage('CALLSIGN', 'OPS', 'EDDF', 'EDDH', None))
    def test_missing_off(self):        self.assertRaises(ValueError, lambda: ProgressMessage('CALLSIGN', 'OPS', 'EDDF', 'EDDH', self._TIME_1, time_on=self._TIME_2))
    def test_missing_on(self):         self.assertRaises(ValueError, lambda: ProgressMessage('CALLSIGN', 'OPS', 'EDDF', 'EDDH', self._TIME_1, time_off=self._TIME_2, time_in=self._TIME_3))
    def test_eta_after_arrival(self):  self.assertRaises(ValueError, lambda: ProgressMessage('CALLSIGN', 'OPS', 'EDDF', 'EDDH', self._TIME_1, self._TIME_5, self._TIME_2, self._TIME_3, self._TIME_4))

class TestProgressMessageRepresentation(unittest.TestCase):
    _TIME_1: time = time(hour=18, minute=20, second=0, tzinfo=UTC)
    _TIME_2: time = time(hour=18, minute=25, second=0, tzinfo=UTC)
    _TIME_3: time = time(hour=18, minute=30, second=0, tzinfo=UTC)
    _TIME_4: time = time(hour=18, minute=35, second=0, tzinfo=UTC)
    
    def test_repr_out_eta(self):
        import datetime # used inside eval()

        expected = ProgressMessage('CALLSIGN', 'OPS', 'AAAA', 'BBBB', self._TIME_1, self._TIME_2)
        actual = eval(repr(expected))
        self.assertEqual(expected, actual)

    def test_repr_out_off_on_in(self):
        import datetime # used inside eval()

        expected = ProgressMessage('CALLSIGN', 'OPS', 'AAAA', 'BBBB', self._TIME_1, None, self._TIME_2, self._TIME_3, self._TIME_4)
        actual = eval(repr(expected))
        self.assertEqual(expected, actual)

class TestProgressMessageFromPacket(unittest.TestCase):
    def test_valid_departure(self):
        actual = ProgressMessage.from_packet('CALLSIGN', 'OPS', 'EDDF/ZZZZ OUT/0000')
        self.assertEqual('EDDF', actual.get_departure())

    def test_valid_arrival(self):
        actual = ProgressMessage.from_packet('CALLSIGN', 'OPS', 'ZZZZ/EDDH OUT/0000')
        self.assertEqual('EDDH', actual.get_arrival())

    def test_time_out(self):
        actual = ProgressMessage.from_packet('CALLSIGN', 'OPS', 'ZZZZ/ZZZZ OUT/1820')
        expected = datetime.strptime('1820', '%H%M').replace(tzinfo=UTC).timetz()
        self.assertEqual(expected, actual.get_time_out())

    def test_time_out_eta(self):
        actual = ProgressMessage.from_packet('CALLSIGN', 'OPS', 'ZZZZ/ZZZZ OUT/0000 ETA/1820')
        expected = datetime.strptime('1820', '%H%M').replace(tzinfo=UTC).timetz()
        self.assertEqual(expected, actual.get_eta())

    def test_time_off(self):
        actual = ProgressMessage.from_packet('CALLSIGN', 'OPS', 'ZZZZ/ZZZZ OUT/0000 OFF/1820')
        expected = datetime.strptime('1820', '%H%M').replace(tzinfo=UTC).timetz()
        self.assertEqual(expected, actual.get_time_off())

    def test_time_off_eta(self):
        actual = ProgressMessage.from_packet('CALLSIGN', 'OPS', 'ZZZZ/ZZZZ OUT/0000 OFF/0001 ETA/1820')
        expected = datetime.strptime('1820', '%H%M').replace(tzinfo=UTC).timetz()
        self.assertEqual(expected, actual.get_eta())

    def test_time_on(self):
        actual = ProgressMessage.from_packet('CALLSIGN', 'OPS', 'ZZZZ/ZZZZ OUT/0000 OFF/0001 ON/1820')
        expected = datetime.strptime('1820', '%H%M').replace(tzinfo=UTC).timetz()
        self.assertEqual(expected, actual.get_time_on())

    def test_time_in(self):
        actual = ProgressMessage.from_packet('CALLSIGN', 'OPS', 'ZZZZ/ZZZZ OUT/0000 OFF/0001 ON/0002 IN/1820')
        expected = datetime.strptime('1820', '%H%M').replace(tzinfo=UTC).timetz()
        self.assertEqual(expected, actual.get_time_in())

    def test_missing_out(self):
        self.assertRaises(ValueError, lambda: ProgressMessage.from_packet('CALLSIGN', 'OPS', 'ZZZZ/ZZZZ'))

    def test_invalid_aprt(self):
        self.assertRaises(ValueError, lambda: ProgressMessage.from_packet('CALLSIGN', 'OPS', 'ZZZZ/EH01'))

    def test_invalid_out(self):
        self.assertRaises(ValueError, lambda: ProgressMessage.from_packet('CALLSIGN', 'OPS', 'ZZZZ/ZZZZ OUT/9999'))

    def test_invalid_off(self):
        self.assertRaises(ValueError, lambda: ProgressMessage.from_packet('CALLSIGN', 'OPS', 'ZZZZ/ZZZZ OUT/0000 OFF/9999'))

    def test_invalid_on(self):
        self.assertRaises(ValueError, lambda: ProgressMessage.from_packet('CALLSIGN', 'OPS', 'ZZZZ/ZZZZ OUT/0000 OFF/0001 ON/9999'))

    def test_special_empty_case(self):
        actual = ProgressMessage.from_packet('CALLSIGN', 'OPS', 'ZZZZ/ZZZZ OUT/1820 OFF/----- ON/----- ETA/-----')
        expected = datetime.strptime('1820', '%H%M').replace(tzinfo=UTC).timetz()
        self.assertEqual(expected, actual.get_time_out())
        self.assertIsNone(actual.get_time_off())
        self.assertIsNone(actual.get_time_on())
        self.assertIsNone(actual.get_eta())
