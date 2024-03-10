from hoppie_connector.Messages import HoppieMessage, AdscMessage
import datetime
import unittest

class TestValidAdscMessage(unittest.TestCase):
    _EXPECTED_TYPE: HoppieMessage.MessageType = HoppieMessage.MessageType.ADS_C
    _EXPECTED_RPT: datetime = datetime.datetime(year=2000, month=2, day=1, hour=18, minute=20, second=0, tzinfo=datetime.UTC)
    _EXPECTED_POS: tuple[float, float] = (-10.0, 10.0)
    _EXPECTED_ALT: float = 3000.0
    _EXPECTED_PACKET: str = 'REPORT CALLSIGN 011820 -10.0000 10.00000 30'
    
    def setUp(self) -> None:
        super().setUp()
        self._UUT = AdscMessage('CALLSIGN', 'OPS', self._EXPECTED_RPT, self._EXPECTED_POS, self._EXPECTED_ALT)

    def test_get_msg_type(self):       self.assertEqual(self._EXPECTED_TYPE, self._UUT.get_msg_type())
    def test_get_report_time(self):    self.assertEqual(self._EXPECTED_RPT, self._UUT.get_report_time())
    def test_get_position(self):       self.assertAlmostEqual(self._EXPECTED_POS, self._UUT.get_position())
    def test_get_heading(self):        self.assertIsNone(self._UUT.get_heading())
    def test_get_remark(self):         self.assertIsNone(self._UUT.get_remark())
    def test_get_packet_content(self): self.assertEqual(self._EXPECTED_PACKET, self._UUT.get_packet_content())

class TestValidAdscMessageHeading(unittest.TestCase):
    _EXPECTED_RPT: datetime = datetime.datetime(year=2000, month=2, day=1, hour=18, minute=20, second=0, tzinfo=datetime.UTC)
    _EXPECTED_POS: tuple[float, float] = (-10.0, 10.0)
    _EXPECTED_ALT: float = 3000.0
    _EXPECTED_HDG: float = 90.0
    _EXPECTED_PACKET: str = 'REPORT CALLSIGN 011820 -10.0000 10.00000 30 90'

    def setUp(self) -> None:
        super().setUp()
        self._UUT = AdscMessage('CALLSIGN', 'OPS', self._EXPECTED_RPT, self._EXPECTED_POS, self._EXPECTED_ALT, self._EXPECTED_HDG)

    def test_get_heading(self):        self.assertAlmostEqual(self._EXPECTED_HDG, self._UUT.get_heading())
    def test_get_packet_content(self): self.assertEqual(self._EXPECTED_PACKET, self._UUT.get_packet_content())

class TestAdscMessageInputValidation(unittest.TestCase):
    _TIME: datetime = datetime.datetime(year=2000, month=2, day=1, hour=18, minute=20, second=0, tzinfo=datetime.UTC)
    
    def test_invalid_negative_lat(self): self.assertRaises(ValueError, lambda: AdscMessage('CALLSIGN', 'OPS', self._TIME, (-91.0, 0), 0))
    def test_invalid_positive_lat(self): self.assertRaises(ValueError, lambda: AdscMessage('CALLSIGN', 'OPS', self._TIME, (+91.0, 0), 0))
    def test_invalid_negative_lon(self): self.assertRaises(ValueError, lambda: AdscMessage('CALLSIGN', 'OPS', self._TIME, (0, -181), 0))
    def test_invalid_positive_lon(self): self.assertRaises(ValueError, lambda: AdscMessage('CALLSIGN', 'OPS', self._TIME, (0, +181), 0))
    def test_invalid_negative_alt(self): self.assertRaises(ValueError, lambda: AdscMessage('CALLSIGN', 'OPS', self._TIME, (0, 0), -1001))
    def test_invalid_positive_alt(self): self.assertRaises(ValueError, lambda: AdscMessage('CALLSIGN', 'OPS', self._TIME, (0, 0), +66001))
    def test_invalid_negative_hdg(self): self.assertRaises(ValueError, lambda: AdscMessage('CALLSIGN', 'OPS', self._TIME, (0, 0), 0, -1))
    def test_invalid_positive_hdg(self): self.assertRaises(ValueError, lambda: AdscMessage('CALLSIGN', 'OPS', self._TIME, (0, 0), 0, 361))
    def test_remark_not_impl(self):      self.assertRaises(NotImplementedError, lambda: AdscMessage('CALLSIGN', 'OPS', self._TIME, (0, 0), 0, 0, 'Test'))