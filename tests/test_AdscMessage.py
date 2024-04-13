from hoppie_connector.Messages import AdscMessage, HoppieMessage, HoppieMessage as Super
import unittest

class TestAdscContractRequestMessage(unittest.TestCase):
    _EXPECTED_TYPE = HoppieMessage.MessageType.ADS_C
    _EXPECTED_SUBTYPE = AdscMessage.AdscMessageType.REQUEST_PERIODIC
    
    def setUp(self) -> None:
        super().setUp()
        self._UUT = AdscMessage('ATC', 'CALLSIGN', self._EXPECTED_SUBTYPE)

    def test_get_type(self):
        self.assertEqual(self._EXPECTED_TYPE, self._UUT.get_msg_type())

    def test_get_adsc_msg_type(self):
        self.assertEqual(self._EXPECTED_SUBTYPE, self._UUT.get_adsc_msg_type())

    def test_get_packet_content(self):
        self.assertEqual(self._EXPECTED_SUBTYPE, self._UUT.get_packet_content())

    def test_hierarchy_super(self):
        self.assertIsInstance(self._UUT, Super)

class TestAdscContractRequestMessageRepresentation(unittest.TestCase):
    def test_repr(self):
        expected = AdscMessage('ATC', 'CALLSIGN', AdscMessage.AdscMessageType.REQUEST_PERIODIC)
        actual = eval(repr(expected))
        self.assertEqual(expected, actual)

class TestAdscContractRequestMessageComparison(unittest.TestCase):
    def test_same(self):
        value1 = AdscMessage('ATC', 'CALLSIGN', AdscMessage.AdscMessageType.REQUEST_PERIODIC)
        value2 = value1
        self.assertEqual(value1, value2)

    def test_equal_content(self):
        value1 = AdscMessage('ATC', 'CALLSIGN', AdscMessage.AdscMessageType.REQUEST_PERIODIC)
        value2 = AdscMessage('ATC', 'CALLSIGN', AdscMessage.AdscMessageType.REQUEST_PERIODIC)
        self.assertEqual(value1, value2)

    def test_differing_subtype(self):
        value1 = AdscMessage('ATC', 'CALLSIGN', AdscMessage.AdscMessageType.REQUEST_PERIODIC)
        value2 = AdscMessage('ATC', 'CALLSIGN', AdscMessage.AdscMessageType.REPORT_PERIODIC)
        self.assertNotEqual(value1, value2)