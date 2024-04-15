from hoppie_connector.Messages import AdscContractCancellationMessage, AdscMessage, AdscMessage as Super
import unittest

class TestAdscContractCancellationMessage(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self._UUT = AdscContractCancellationMessage('CALLSIGN', 'ATC')

    def test_get_adsc_msg_type(self):
        self.assertEqual(AdscMessage.AdscMessageType.REQUEST_CANCEL, self._UUT.get_adsc_msg_type())

    def test_get_packet_content(self):
        self.assertEqual('REQUEST CANCEL', self._UUT.get_packet_content())

    def test_hierarchy_super(self):
        self.assertIsInstance(self._UUT, Super)

class TestAdscContractCancellationMessageRepresentation(unittest.TestCase):
    def test_repr(self):
        expected = AdscContractCancellationMessage('CALLSIGN', 'ATC')
        actual = eval(repr(expected))
        self.assertEqual(expected, actual)

class TestAAdscContractCancellationMessageFromPacket(unittest.TestCase):
    def test_from_packet(self):
        expected = AdscContractCancellationMessage('CALLSIGN', 'ATC')
        actual = AdscContractCancellationMessage.from_packet('CALLSIGN', 'ATC')
        self.assertEqual(expected, actual)

class TestAdscContractCancellationMessageComparison(unittest.TestCase):
    def test_same(self):
        value1 = AdscContractCancellationMessage('CALLSIGN', 'ATC')
        value2 = value1
        self.assertEqual(value1, value2)

    def test_equal_content(self):
        value1 = AdscContractCancellationMessage('CALLSIGN', 'ATC')
        value2 = AdscContractCancellationMessage('CALLSIGN', 'ATC')
        self.assertEqual(value1, value2)