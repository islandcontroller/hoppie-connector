from hoppie_connector.Messages import HoppieMessage, PollMessage
import unittest

class TestValidPollMessage(unittest.TestCase):
    _EXPECTED_TO: str = 'SERVER'
    _EXPECTED_TYPE: HoppieMessage.MessageType = HoppieMessage.MessageType.POLL
    _EXPECTED_PACKET: str = ''

    def setUp(self) -> None:
        super().setUp()
        self._UUT = PollMessage('OPS')

    def test_get_to_name(self):  self.assertEqual(self._EXPECTED_TO,   self._UUT.get_to_name())
    def test_get_msg_type(self): self.assertEqual(self._EXPECTED_TYPE, self._UUT.get_msg_type())
