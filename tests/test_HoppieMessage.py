from hoppie_connector.Messages import HoppieMessage
import unittest

class TestValidHoppieMessage(unittest.TestCase):
    _EXPECTED_FROM: str = 'CALLSIGN'
    _EXPECTED_TO: str = 'OPS'
    _EXPECTED_TYPE: HoppieMessage.MessageType = HoppieMessage.MessageType.TELEX
    _EXPECTED_PACKET: str = ''
    _EXPECTED_MSG_PARAM: dict = {
        'from': _EXPECTED_FROM,
        'to': _EXPECTED_TO,
        'type': _EXPECTED_TYPE.value,
        'packet': _EXPECTED_PACKET
    }

    def setUp(self) -> None:
        super().setUp()
        self._UUT = HoppieMessage(self._EXPECTED_FROM, self._EXPECTED_TO, self._EXPECTED_TYPE)

    def test_get_from_name(self):      self.assertEqual(self._EXPECTED_FROM,      self._UUT.get_from_name())
    def test_get_to_name(self):        self.assertEqual(self._EXPECTED_TO,        self._UUT.get_to_name())
    def test_get_msg_type(self):       self.assertEqual(self._EXPECTED_TYPE,      self._UUT.get_msg_type())
    def test_get_packet_content(self): self.assertEqual(self._EXPECTED_PACKET,    self._UUT.get_packet_content())
    def test_get_msg_params(self):     self.assertEqual(self._EXPECTED_MSG_PARAM, self._UUT.get_msg_params())

class TestHoppieMessageInputValidation(unittest.TestCase):
    def test_empty_from_name(self):   self.assertRaises(ValueError, lambda: HoppieMessage('',          'OPS',       HoppieMessage.MessageType.TELEX))
    def test_empty_to_name(self):     self.assertRaises(ValueError, lambda: HoppieMessage('CALLSIGN',  '',          HoppieMessage.MessageType.TELEX))
    def test_from_too_long(self):     self.assertRaises(ValueError, lambda: HoppieMessage('123456789', 'OPS',       HoppieMessage.MessageType.TELEX))
    def test_to_too_long(self):       self.assertRaises(ValueError, lambda: HoppieMessage('CALLSIGN',  '123456789', HoppieMessage.MessageType.TELEX))
    def test_invalid_from_char(self): self.assertRaises(ValueError, lambda: HoppieMessage('D-ABCD',    'OPS',       HoppieMessage.MessageType.TELEX))
    def test_invalid_to_char(self):   self.assertRaises(ValueError, lambda: HoppieMessage('CALLSIGN',  'ops',       HoppieMessage.MessageType.TELEX))
    def test_invalid_type(self):      self.assertRaises(ValueError, lambda: HoppieMessage('CALLSIGN',  'OPS',       0))
    def test_special_from_all(self):  self.assertIsInstance(HoppieMessage('ALL-CALLSIGNS', 'OPS', HoppieMessage.MessageType.TELEX), HoppieMessage)
    def test_special_to_all(self):    self.assertIsInstance(HoppieMessage('OPS', 'ALL-CALLSIGNS', HoppieMessage.MessageType.TELEX), HoppieMessage)
