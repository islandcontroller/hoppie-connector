from hoppie_connector.Messages import HoppieMessage
from hoppie_connector.Responses import HoppieResponseParser, PeekResponseParser, PollResponseParser, PingResponseParser, HoppieResponseParserFactory
import unittest

class TestHoppieResponseParserFactory(unittest.TestCase):
    def test_create_poll(self):  self.assertIsInstance(HoppieResponseParserFactory().create_parser(HoppieMessage.MessageType.POLL), PollResponseParser)
    def test_create_peek(self):  self.assertIsInstance(HoppieResponseParserFactory().create_parser(HoppieMessage.MessageType.PEEK), PeekResponseParser)
    def test_create_ping(self):  self.assertIsInstance(HoppieResponseParserFactory().create_parser(HoppieMessage.MessageType.PING), PingResponseParser)
    def test_create_telex(self): self.assertIsInstance(HoppieResponseParserFactory().create_parser(HoppieMessage.MessageType.TELEX), HoppieResponseParser)