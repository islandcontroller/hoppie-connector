from hoppie_connector.Messages import HoppieMessage, ProgressMessage
import datetime
import unittest

class TestValidProgressMessage(unittest.TestCase):
    _EXPECTED_TYPE: HoppieMessage.MessageType = HoppieMessage.MessageType.PROGRESS
    _EXPECTED_DEP: str = 'EDDF'
    _EXPECTED_ARR: str = 'EDDH'
    _EXPECTED_OUT: datetime = datetime.datetime(year=2000, month=1, day=1, hour=18, minute=20, second=0, tzinfo=datetime.UTC)
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

class TestValidProgressMessageEta(unittest.TestCase):
    _EXPECTED_OUT: datetime = datetime.datetime(year=2000, month=1, day=1, hour=18, minute=20, second=0, tzinfo=datetime.UTC)
    _EXPECTED_ETA: datetime = _EXPECTED_OUT + datetime.timedelta(minutes=5)
    _EXPECTED_PACKET: str = 'EDDF/EDDH OUT/1820 ETA/1825'

    def setUp(self) -> None:
        super().setUp()
        self._UUT = ProgressMessage('CALLSIGN', 'OPS', 'EDDF', 'EDDH', self._EXPECTED_OUT, self._EXPECTED_ETA)

    def test_get_eta(self):            self.assertEqual(self._EXPECTED_ETA, self._UUT.get_eta())
    def test_get_packet_content(self): self.assertEqual(self._EXPECTED_PACKET, self._UUT.get_packet_content())

class TestValidProgressMessageOff(unittest.TestCase):
    _EXPECTED_OUT: datetime = datetime.datetime(year=2000, month=1, day=1, hour=18, minute=20, second=0, tzinfo=datetime.UTC)
    _EXPECTED_OFF: datetime = _EXPECTED_OUT + datetime.timedelta(minutes=5)
    _EXPECTED_PACKET: str = 'EDDF/EDDH OUT/1820 OFF/1825'

    def setUp(self) -> None:
        super().setUp()
        self._UUT = ProgressMessage('CALLSIGN', 'OPS', 'EDDF', 'EDDH', self._EXPECTED_OUT, time_off=self._EXPECTED_OFF)

    def test_get_time_off(self):       self.assertEqual(self._EXPECTED_OFF, self._UUT.get_time_off())
    def test_get_packet_content(self): self.assertEqual(self._EXPECTED_PACKET, self._UUT.get_packet_content())

class TestValidProgressMessageOffEta(unittest.TestCase):
    _EXPECTED_OUT: datetime = datetime.datetime(year=2000, month=1, day=1, hour=18, minute=20, second=0, tzinfo=datetime.UTC)
    _EXPECTED_OFF: datetime = _EXPECTED_OUT + datetime.timedelta(minutes=5)
    _EXPECTED_ETA: datetime = _EXPECTED_OFF + datetime.timedelta(minutes=5)
    _EXPECTED_PACKET: str = 'EDDF/EDDH OUT/1820 OFF/1825 ETA/1830'

    def setUp(self) -> None:
        super().setUp()
        self._UUT = ProgressMessage('CALLSIGN', 'OPS', 'EDDF', 'EDDH', self._EXPECTED_OUT, self._EXPECTED_ETA, self._EXPECTED_OFF)

    def test_get_packet_content(self): self.assertEqual(self._EXPECTED_PACKET, self._UUT.get_packet_content())

class TestValidProgressMessageOn(unittest.TestCase):
    _EXPECTED_OUT: datetime = datetime.datetime(year=2000, month=1, day=1, hour=18, minute=20, second=0, tzinfo=datetime.UTC)
    _EXPECTED_OFF: datetime = _EXPECTED_OUT + datetime.timedelta(minutes=5)
    _EXPECTED_ON: datetime = _EXPECTED_OFF + datetime.timedelta(minutes=5)
    _EXPECTED_PACKET: str = 'EDDF/EDDH OUT/1820 OFF/1825 ON/1830'

    def setUp(self) -> None:
        super().setUp()
        self._UUT = ProgressMessage('CALLSIGN', 'OPS', 'EDDF', 'EDDH', self._EXPECTED_OUT, time_off=self._EXPECTED_OFF, time_on=self._EXPECTED_ON)

    def test_get_packet_content(self): self.assertEqual(self._EXPECTED_PACKET, self._UUT.get_packet_content())

class TestValidProgressMessageIn(unittest.TestCase):
    _EXPECTED_OUT: datetime = datetime.datetime(year=2000, month=1, day=1, hour=18, minute=20, second=0, tzinfo=datetime.UTC)
    _EXPECTED_OFF: datetime = _EXPECTED_OUT + datetime.timedelta(minutes=5)
    _EXPECTED_ON: datetime = _EXPECTED_OFF + datetime.timedelta(minutes=5)
    _EXPECTED_IN: datetime = _EXPECTED_ON + datetime.timedelta(minutes=5)
    _EXPECTED_PACKET: str = 'EDDF/EDDH OUT/1820 OFF/1825 ON/1830 IN/1835'

    def setUp(self) -> None:
        super().setUp()
        self._UUT = ProgressMessage('CALLSIGN', 'OPS', 'EDDF', 'EDDH', self._EXPECTED_OUT, time_off=self._EXPECTED_OFF, time_on=self._EXPECTED_ON, time_in=self._EXPECTED_IN)

    def test_get_packet_content(self): self.assertEqual(self._EXPECTED_PACKET, self._UUT.get_packet_content())

class TestProgressMessageInputValidation(unittest.TestCase):
    _TIME_1: datetime = datetime.datetime(year=2000, month=1, day=1, hour=18, minute=20, second=0, tzinfo=datetime.UTC)
    _TIME_2: datetime = _TIME_1 + datetime.timedelta(minutes=5)
    _TIME_3: datetime = _TIME_2 + datetime.timedelta(minutes=5)
    _TIME_4: datetime = _TIME_3 + datetime.timedelta(minutes=5)

    def test_invalid_dep_code(self):   self.assertRaises(ValueError, lambda: ProgressMessage('CALLSIGN', 'OPS', 'EH02', 'EDDH', self._TIME_1))
    def test_invalid_arr_code(self):   self.assertRaises(ValueError, lambda: ProgressMessage('CALLSIGN', 'OPS', 'EDDF', 'abc',  self._TIME_1))
    def test_missing_off(self):        self.assertRaises(ValueError, lambda: ProgressMessage('CALLSIGN', 'OPS', 'EDDF', 'EDDH', self._TIME_1, time_on=self._TIME_2))
    def test_missing_on(self):         self.assertRaises(ValueError, lambda: ProgressMessage('CALLSIGN', 'OPS', 'EDDF', 'EDDH', self._TIME_1, time_off=self._TIME_2, time_in=self._TIME_3))
    def test_off_before_out(self):     self.assertRaises(ValueError, lambda: ProgressMessage('CALLSIGN', 'OPS', 'EDDF', 'EDDH', self._TIME_2, time_off=self._TIME_1))
    def test_on_before_off(self):      self.assertRaises(ValueError, lambda: ProgressMessage('CALLSIGN', 'OPS', 'EDDF', 'EDDH', self._TIME_1, time_off=self._TIME_3, time_on=self._TIME_2))
    def test_in_before_on(self):       self.assertRaises(ValueError, lambda: ProgressMessage('CALLSIGN', 'OPS', 'EDDF', 'EDDH', self._TIME_1, time_off=self._TIME_2, time_on=self._TIME_4, time_in=self._TIME_3))
    def test_eta_before_out(self):     self.assertRaises(ValueError, lambda: ProgressMessage('CALLSIGN', 'OPS', 'EDDF', 'EDDH', self._TIME_2, self._TIME_1))
    def test_eta_before_off(self):     self.assertRaises(ValueError, lambda: ProgressMessage('CALLSIGN', 'OPS', 'EDDF', 'EDDH', self._TIME_1, self._TIME_2, self._TIME_3))
    def test_eta_after_arrival(self):  self.assertRaises(ValueError, lambda: ProgressMessage('CALLSIGN', 'OPS', 'EDDF', 'EDDH', self._TIME_1, self._TIME_4, self._TIME_2, self._TIME_3))