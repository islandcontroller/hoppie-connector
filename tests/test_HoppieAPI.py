from hoppie_connector.API import HoppieAPI
from hoppie_connector.Messages import PeekMessage, PollMessage, TelexMessage
from hoppie_connector.Responses import SuccessResponse, ErrorResponse
from responses import matchers
import responses
import unittest

class TestHoppieApiURL(unittest.TestCase):
    @responses.activate
    def test_default_url(self):
        expected_url = 'https://www.hoppie.nl/acars/system/connect.html'
        expected_logon = 'AbCdef12358'
        responses.get(expected_url, body='ok')

        HoppieAPI(expected_logon).connect(PeekMessage('CALLSIGN'))

        responses.assert_call_count(f"{expected_url}?logon={expected_logon}&from=CALLSIGN&to=SERVER&type=peek&packet=", 1)

    @responses.activate
    def test_custom_url(self):
        expected_url = 'https://www.example.com/'
        expected_logon = 'AbCdef12358'
        responses.get(expected_url, body='ok')

        HoppieAPI(expected_logon, expected_url).connect(PeekMessage('CALLSIGN'))

        responses.assert_call_count(f"{expected_url}?logon={expected_logon}&from=CALLSIGN&to=SERVER&type=peek&packet=", 1)

class TestHoppieApiConnect(unittest.TestCase):
    _URL: str = 'http://example.com'

    @responses.activate
    def test_error_illegal_logon_code(self):
        responses.get(self._URL, body='error {illegal logon code}')

        actual: ErrorResponse = HoppieAPI('', self._URL).connect(PeekMessage('CALLSIGN'))
        
        self.assertIsInstance(actual, ErrorResponse)
        self.assertEqual('illegal logon code', actual.get_reason())

    @responses.activate
    def test_success_empty(self):
        responses.get(self._URL, body='ok')

        actual: SuccessResponse = HoppieAPI('', self._URL).connect(PeekMessage('CALLSIGN'))
        
        self.assertIsInstance(actual, SuccessResponse)
        self.assertListEqual([], actual.get_items())

    @responses.activate
    def test_success_poll(self):
        responses.get(self._URL, body='ok {OPS telex {MESSAGE 1}} {OPS telex {MESSAGE 2}}')
        expected_items = [
            {'id': None, 'from': 'OPS', 'type': 'telex', 'packet': 'MESSAGE 1'},
            {'id': None, 'from': 'OPS', 'type': 'telex', 'packet': 'MESSAGE 2'}
        ]

        actual: SuccessResponse = HoppieAPI('', self._URL).connect(PollMessage('CALLSIGN'))
        
        self.assertIsInstance(actual, SuccessResponse)
        self.assertListEqual(expected_items, actual.get_items())

    @responses.activate
    def test_success_peek(self):
        responses.get(self._URL, body='ok {1 OPS telex {MESSAGE 1}} {2 OPS telex {MESSAGE 2}}')
        expected_items = [
            {'id': 1, 'from': 'OPS', 'type': 'telex', 'packet': 'MESSAGE 1'},
            {'id': 2, 'from': 'OPS', 'type': 'telex', 'packet': 'MESSAGE 2'}
        ]

        actual: SuccessResponse = HoppieAPI('', self._URL).connect(PeekMessage('CALLSIGN'))
        
        self.assertIsInstance(actual, SuccessResponse)
        self.assertListEqual(expected_items, actual.get_items())