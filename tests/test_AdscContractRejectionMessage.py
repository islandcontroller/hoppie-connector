from hoppie_connector.Messages import AdscContractRejectionMessage, AdscMessage, AdscMessage as Super
import unittest

class TestAdscContractRejectionMessage(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self._UUT = AdscContractRejectionMessage('CALLSIGN', 'ATC')

    def test_get_adsc_msg_type(self):
        self.assertEqual(AdscMessage.AdscMessageType.REJECT, self._UUT.get_adsc_msg_type())

    def test_get_packet_content(self):
        self.assertEqual('REJECT', self._UUT.get_packet_content())

    def test_hierarchy_super(self):
        self.assertIsInstance(self._UUT, Super)

class TestAdscContractRejectionMessageRepresentation(unittest.TestCase):
    def test_repr(self):
        expected = AdscContractRejectionMessage('CALLSIGN', 'ATC')
        actual = eval(repr(expected))
        self.assertEqual(expected, actual)

class TestAdscContractRejectionMessageFromPacket(unittest.TestCase):
    def test_from_packet(self):
        expected = AdscContractRejectionMessage('CALLSIGN', 'ATC')
        actual = AdscContractRejectionMessage.from_packet('CALLSIGN', 'ATC')
        self.assertEqual(expected, actual)

class TestAdscContractRejectionMessageComparison(unittest.TestCase):
    def test_same(self):
        value1 = AdscContractRejectionMessage('CALLSIGN', 'ATC')
        value2 = value1
        self.assertEqual(value1, value2)

    def test_equal_content(self):
        value1 = AdscContractRejectionMessage('CALLSIGN', 'ATC')
        value2 = AdscContractRejectionMessage('CALLSIGN', 'ATC')
        self.assertEqual(value1, value2)