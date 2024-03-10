from hoppie_connector.Messages import HoppieMessage, TelexMessage
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

class TestTelexMessageInputValidation(unittest.TestCase):
    def test_message_too_long(self):     self.assertRaises(ValueError, lambda: TelexMessage('CALLSIGN', 'OPS', 221 * 'a'))
    def test_invalid_message_char(self): self.assertRaises(ValueError, lambda: TelexMessage('CALLSIGN', 'OPS', 'ä'))
