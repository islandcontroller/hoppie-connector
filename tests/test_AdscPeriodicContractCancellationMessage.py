from hoppie_connector.Messages import AdscPeriodicContractCancellationMessage, AdscMessage, AdscMessage as Super
import unittest

class TestAdscPeriodicContractCancellationMessage(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self._UUT = AdscPeriodicContractCancellationMessage('CALLSIGN', 'ATC')

    def test_get_adsc_msg_type(self):
        self.assertEqual(AdscMessage.AdscMessageType.CANCEL_PERIODIC, self._UUT.get_adsc_msg_type())

    def test_get_packet_content(self):
        self.assertEqual('REPORT CANCEL', self._UUT.get_packet_content())

    def test_hierarchy_super(self):
        self.assertIsInstance(self._UUT, Super)

class TestAdscPeriodicContractRequestMessageRepresentation(unittest.TestCase):
    def test_repr(self):
        expected = AdscPeriodicContractCancellationMessage('CALLSIGN', 'ATC')
        actual = eval(repr(expected))
        self.assertEqual(expected, actual)

class TestAdscPeriodicContractRequestMessageFromPacket(unittest.TestCase):
    def test_from_packet(self):
        expected = AdscPeriodicContractCancellationMessage('CALLSIGN', 'ATC')
        actual = AdscPeriodicContractCancellationMessage.from_packet('CALLSIGN', 'ATC')
        self.assertEqual(expected, actual)

class TestAdscPeriodicContractRequestMessageComparison(unittest.TestCase):
    def test_same(self):
        value1 = AdscPeriodicContractCancellationMessage('CALLSIGN', 'ATC')
        value2 = value1
        self.assertEqual(value1, value2)

    def test_equal_content(self):
        value1 = AdscPeriodicContractCancellationMessage('CALLSIGN', 'ATC')
        value2 = AdscPeriodicContractCancellationMessage('CALLSIGN', 'ATC')
        self.assertEqual(value1, value2)