from hoppie_connector.Messages import PingMessage, HoppieMessage, HoppieMessage as Super
import unittest

class TestValidPingMessage(unittest.TestCase):
    _EXPECTED_TO: str = 'SERVER'
    _EXPECTED_TYPE: HoppieMessage.MessageType = HoppieMessage.MessageType.PING
    _EXPECTED_STATIONS: list[str] = []
    _EXPECTED_PACKET: str = ''

    def setUp(self) -> None:
        super().setUp()
        self._UUT = PingMessage('STATION')

    def test_get_to_name(self):        self.assertEqual(self._EXPECTED_TO,       self._UUT.get_to_name())
    def test_get_msg_type(self):       self.assertEqual(self._EXPECTED_TYPE,     self._UUT.get_msg_type())
    def test_get_stations(self):       self.assertEqual(self._EXPECTED_STATIONS, self._UUT.get_stations())
    def test_get_packet_content(self): self.assertEqual(self._EXPECTED_PACKET,   self._UUT.get_packet_content())
    def test_hierarchy_super(self):    self.assertIsInstance(self._UUT, Super)

class TestPingMessageInputValidation(unittest.TestCase):
    def test_invalid_station(self):         self.assertRaises(ValueError, lambda: PingMessage('STATION', '123456789'))
    def test_invalid_station_in_list(self): self.assertRaises(ValueError, lambda: PingMessage('STATION', ['CALLSIGN', '123456789']))
    def test_too_many_stations(self):       self.assertRaises(ValueError, lambda: PingMessage('STATION', 25 * ['CALLSIGN']))
    def test_special_all_stations(self):
        expected = ['ALL-CALLSIGNS']
        acutal = PingMessage('STATION', '*')
        self.assertEqual(expected, acutal.get_stations())

class TestPingMessageRepresentation(unittest.TestCase):
    def test_repr(self):
        expected = PingMessage('STATION')
        actual = eval(repr(expected))
        self.assertEqual(expected, actual)