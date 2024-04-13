from hoppie_connector.Messages import TelexMessage, HoppieMessage, HoppieMessage as Super
import unittest

class TestValidTelexMessage(unittest.TestCase):
    _EXPECTED_TYPE: HoppieMessage.MessageType = HoppieMessage.MessageType.TELEX
    _EXPECTED_MESSAGE: str = 'Hello 123'
    _EXPECTED_PACKET: str = 'HELLO 123'

    def setUp(self) -> None:
        super().setUp()
        self._UUT = TelexMessage('CALLSIGN', 'OPS', self._EXPECTED_MESSAGE)

    def test_get_msg_type(self):       self.assertEqual(self._EXPECTED_TYPE,    self._UUT.get_msg_type())
    def test_get_message(self):        self.assertEqual(self._EXPECTED_MESSAGE, self._UUT.get_message())
    def test_get_packet_content(self): self.assertEqual(self._EXPECTED_PACKET,  self._UUT.get_packet_content())
    def test_hierarchy_super(self):    self.assertIsInstance(self._UUT, Super)

class TestTelexMessageInputValidation(unittest.TestCase):
    def test_message_too_long(self):     self.assertRaises(ValueError, lambda: TelexMessage('CALLSIGN', 'OPS', 221 * 'a'))
    def test_invalid_message_char(self): self.assertRaises(ValueError, lambda: TelexMessage('CALLSIGN', 'OPS', 'ä'))

class TestTelexMessageRepresentation(unittest.TestCase):
    def test_repr(self):
        expected = TelexMessage('CALLSIGN', 'OPS', 'Message')
        actual = eval(repr(expected))
        self.assertEqual(expected, actual)

class TestTelexMessageFromPacket(unittest.TestCase):
    def test_empty_message(self):
        expected: str = ''
        actual: TelexMessage = TelexMessage.from_packet('CALLSIGN', 'OPS', expected)
        self.assertEqual(expected, actual.get_message())

    def test_valid_message(self):
        expected: str = 'Message'
        actual: TelexMessage = TelexMessage.from_packet('CALLSIGN', 'OPS', expected)
        self.assertEqual(expected, actual.get_message())

    def test_oversize_content(self):
        self.assertRaises(ValueError, lambda: TelexMessage.from_packet('CALLSIGN', 'OPS', 221*'a'))
