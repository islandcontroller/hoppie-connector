from hoppie_connector.Messages import PeekMessage, HoppieMessage, HoppieMessage as Super
import unittest

class TestValidPeekMessage(unittest.TestCase):
    _EXPECTED_TO: str = 'SERVER'
    _EXPECTED_TYPE: HoppieMessage.MessageType = HoppieMessage.MessageType.PEEK
    _EXPECTED_PACKET: str = ''

    def setUp(self) -> None:
        super().setUp()
        self._UUT = PeekMessage('OPS')

    def test_get_to_name(self):     self.assertEqual(self._EXPECTED_TO,   self._UUT.get_to_name())
    def test_get_msg_type(self):    self.assertEqual(self._EXPECTED_TYPE, self._UUT.get_msg_type())
    def test_hierarchy_super(self): self.assertIsInstance(self._UUT, Super)

class TestPeekMessageRepresentation(unittest.TestCase):
    def test_repr(self):
        expected = PeekMessage('OPS')
        actual = eval(repr(expected))
        self.assertEqual(expected, actual)