from hoppie_connector.Messages import AdscPeriodicContractRequestMessage, AdscMessage, AdscMessage as Super
import unittest

class TestAdscPeriodicContractRequestMessage(unittest.TestCase):
    _EXPECTED_INTERVAL: int = 120
    
    def setUp(self) -> None:
        super().setUp()
        self._UUT = AdscPeriodicContractRequestMessage('ATC', 'CALLSIGN', self._EXPECTED_INTERVAL)

    def test_get_adsc_msg_type(self):
        self.assertEqual(AdscMessage.AdscMessageType.REQUEST_PERIODIC, self._UUT.get_adsc_msg_type())

    def test_get_interval(self):
        self.assertEqual(self._EXPECTED_INTERVAL, self._UUT.get_interval())

    def test_not_demand_contract_request(self):
        self.assertFalse(self._UUT.is_demand_contract_request())

    def test_get_packet_content(self):
        self.assertEqual('REQUEST PERIODIC 120', self._UUT.get_packet_content())

    def test_hierarchy_super(self):
        self.assertIsInstance(self._UUT, Super)

class TestAdscPeriodicContractRequestMessageDemandRequest(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self._UUT = AdscPeriodicContractRequestMessage('ATC', 'CALLSIGN', 0)

    def test_is_demand_contract_request(self):
        self.assertTrue(self._UUT.is_demand_contract_request())

class TestAdscPeriodicContractRequestMessageErrorHandling(unittest.TestCase):
    def test_invalid_interval(self):
        self.assertRaises(ValueError, lambda: AdscPeriodicContractRequestMessage('ATC', 'CALLSIGN', -1))

class TestAdscPeriodicContractRequestMessageRepresentation(unittest.TestCase):
    def test_repr(self):
        expected = AdscPeriodicContractRequestMessage('ATC', 'CALLSIGN', 120)
        actual = eval(repr(expected))
        self.assertEqual(expected, actual)

class TestAdscPeriodicContractRequestMessageFromPacket(unittest.TestCase):
    def test_from_packet(self):
        expected = AdscPeriodicContractRequestMessage('ATC', 'CALLSIGN', 120)
        actual = AdscPeriodicContractRequestMessage.from_packet('ATC', 'CALLSIGN', "REQUEST PERIODIC 120")
        self.assertEqual(expected, actual)

    def test_invalid_format(self):
        self.assertRaises(ValueError, lambda: AdscPeriodicContractRequestMessage.from_packet('ATC', 'CALLSIGN', 'REQUEST PERIODIC'))

class TestAdscPeriodicContractRequestMessageComparison(unittest.TestCase):
    def test_same(self):
        value1 = AdscPeriodicContractRequestMessage('ATC', 'CALLSIGN', 120)
        value2 = value1
        self.assertEqual(value1, value2)

    def test_equal_content(self):
        value1 = AdscPeriodicContractRequestMessage('ATC', 'CALLSIGN', 120)
        value2 = AdscPeriodicContractRequestMessage('ATC', 'CALLSIGN', 120)
        self.assertEqual(value1, value2)

    def test_differing(self):
        value1 = AdscPeriodicContractRequestMessage('ATC', 'CALLSIGN', 120)
        value2 = AdscPeriodicContractRequestMessage('ATC', 'CALLSIGN', 90)
        self.assertNotEqual(value1, value2)