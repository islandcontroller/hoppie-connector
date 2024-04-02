from hoppie_connector.Messages import HoppieMessage
import copy
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
    def test_invalid_from_all(self):  self.assertRaises(ValueError, lambda: HoppieMessage('ALL-CALLSIGNS', 'OPS',   HoppieMessage.MessageType.TELEX))
    def test_invalid_to_all(self):    self.assertRaises(ValueError, lambda: HoppieMessage('OPS', 'ALL-CALLSIGNS',   HoppieMessage.MessageType.TELEX))

class TestHoppieMessageComparison(unittest.TestCase):
    def test_same(self):
        value1 = HoppieMessage('CALLSIGN', 'OPS', HoppieMessage.MessageType.TELEX)
        value2 = value1
        self.assertEqual(value1, value2)

    def test_equal_contents(self):
        value1 = HoppieMessage('CALLSIGN', 'OPS', HoppieMessage.MessageType.TELEX)
        value2 = HoppieMessage('CALLSIGN', 'OPS', HoppieMessage.MessageType.TELEX)
        self.assertEqual(value1, value2)

    def test_differing(self):
        value1 = HoppieMessage('CALLSIGN', 'OPS', HoppieMessage.MessageType.TELEX)
        value2 = HoppieMessage('CALLSIGN', 'OPS', HoppieMessage.MessageType.PEEK)
        self.assertNotEqual(value1, value2)

class TestHoppieMessageRepresentation(unittest.TestCase):
    def test_str(self):
        expected = 'CALLSIGN -> OPS [TELEX] '
        actual = str(HoppieMessage('CALLSIGN', 'OPS', HoppieMessage.MessageType.TELEX))
        self.assertEqual(expected, actual)

    def test_msg_type_repr(self):
        expected = HoppieMessage.MessageType.TELEX
        actual = eval(repr(expected))
        self.assertEqual(expected, actual)

    def test_msg_repr(self):
        expected = HoppieMessage('CALLSIGN', 'OPS', HoppieMessage.MessageType.TELEX)
        actual = eval(repr(expected))
        self.assertEqual(expected, actual)

class TestHoppieMessageType(unittest.TestCase):
    def test_compare_same(self):
        value1 = HoppieMessage.MessageType.ADS_C
        value2 = value1
        self.assertEqual(value1, value2)

    def test_compare_equal_enum(self):
        value1 = HoppieMessage.MessageType.ADS_C
        value2 = HoppieMessage.MessageType.ADS_C
        self.assertEqual(value1, value2)

    def test_compare_equal_str(self):
        value1 = HoppieMessage.MessageType.ADS_C
        value2 = 'ads-c'
        self.assertEqual(value1, value2)
    
    def test_repr(self):
        expected = HoppieMessage.MessageType.ADS_C
        actual = eval(repr(expected))
        self.assertEqual(expected, actual)