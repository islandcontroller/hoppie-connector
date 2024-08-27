from hoppie_connector.Messages import CpdlcMessage, HoppieMessage, HoppieMessage as Super
from hoppie_connector.CPDLC import CpdlcResponseRequirement as RR
import unittest

class TestCpdlcMessage(unittest.TestCase):
    _EXPECTED_TYPE: HoppieMessage.MessageType = HoppieMessage.MessageType.CPDLC
    _EXPECTED_MIN: int = 1
    _EXPECTED_RR: RR = RR.NE
    _EXPECTED_MESSAGE: str = 'DEPART REQUEST STATUS . FSM 1957 240826 ENGM @SAS385@ RCD RECEIVED @REQUEST BEING PROCESSED @STANDBY'
    _EXPECTED_PACKET: str = '/data2/1//NE/DEPART REQUEST STATUS . FSM 1957 240826 ENGM @SAS385@ RCD RECEIVED @REQUEST BEING PROCESSED @STANDBY'

    def setUp(self) -> None:
        super().setUp()
        self._UUT = CpdlcMessage('ATSU', 'CALLSIGN', self._EXPECTED_MIN, self._EXPECTED_RR, self._EXPECTED_MESSAGE)

    def test_get_msg_type(self):       self.assertEqual(self._EXPECTED_TYPE,    self._UUT.get_msg_type())
    def test_get_min(self):            self.assertEqual(self._EXPECTED_MIN,     self._UUT.get_min())
    def test_get_rr(self):             self.assertEqual(self._EXPECTED_RR,      self._UUT.get_rr())
    def test_get_message(self):        self.assertEqual(self._EXPECTED_MESSAGE, self._UUT.get_message())
    def test_get_mrn(self):            self.assertIsNone(self._UUT.get_mrn())
    def test_get_packet_content(self): self.assertEqual(self._EXPECTED_PACKET,  self._UUT.get_packet_content())
    def test_hierarchy_super(self):    self.assertIsInstance(self._UUT, Super)

class TestCpdlcMessageWithMRN(unittest.TestCase):
    _EXPECTED_MRN: int = 19
    _EXPECTED_PACKET: str = '/data2/6/19/N/WILCO'

    def setUp(self) -> None:
        super().setUp()
        self._UUT = CpdlcMessage('CALLSIGN', 'ATSU', 6, RR.N, 'WILCO', self._EXPECTED_MRN)

    def test_get_mrn(self):            self.assertEqual(self._EXPECTED_MRN, self._UUT.get_mrn())
    def test_get_packet_content(self): self.assertEqual(self._EXPECTED_PACKET,  self._UUT.get_packet_content())

class TestCpdlcMessageRepresentation(unittest.TestCase):
    def test_repr(self):
        from hoppie_connector.CPDLC import CpdlcResponseRequirement # used inside eval()

        expected = CpdlcMessage('ATSU', 'CALLSIGN', 1, RR.NE, 'TEST MSG')
        actual = eval(repr(expected))
        self.assertEqual(expected, actual)

    def test_repr_mrn(self):
        from hoppie_connector.CPDLC import CpdlcResponseRequirement # used inside eval()
        
        expected = CpdlcMessage('ATSU', 'CALLSIGN', 1, RR.Y, 'TEST MSG', 12)
        actual = eval(repr(expected))
        self.assertEqual(expected, actual)

class TestCpdlcMessageInputValidation(unittest.TestCase):
    def test_invalid_min(self): self.assertRaises(ValueError, lambda: CpdlcMessage('CALLSIGN', 'ATSU', -1, RR.A_N, 'MSG'))
    def test_invalid_mrn(self): self.assertRaises(ValueError, lambda: CpdlcMessage('CALLSIGN', 'ATSU', 1, RR.A_N, 'MSG', -1))
    def test_invalid_msg(self): self.assertRaises(ValueError, lambda: CpdlcMessage('CALLSIGN', 'ATSU', 1, RR.A_N, 'UNSUPPORTED / CHAR'))
    def test_invalid_rr(self):  self.assertRaises(ValueError, lambda: CpdlcMessage('CALLSIGN', 'ATSU', 1, 'INVALID', 'MSG'))

class TestCpdlcMessageFromPacket(unittest.TestCase):
    def test_valid(self):
        expected = CpdlcMessage('CALLSIGN', 'ATSU', 1, RR.AFFIRM_NEGATIVE, 'MESSAGE STR')
        actual = CpdlcMessage.from_packet('CALLSIGN', 'ATSU', '/data2/1//AN/MESSAGE STR')
        self.assertEqual(expected, actual)

    def test_malformed(self):
        self.assertRaises(ValueError, lambda: CpdlcMessage.from_packet('CALLSIGN', 'ATSU', '//1/N/WILCO'))