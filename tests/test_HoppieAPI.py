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
        expected_url = 'https://www.example.com/1'
        expected_logon = 'AbCdef12358'
        responses.get(expected_url, body='ok')

        HoppieAPI(expected_logon, expected_url).connect(PeekMessage('CALLSIGN'))

        responses.assert_call_count(f"{expected_url}?logon={expected_logon}&from=CALLSIGN&to=SERVER&type=peek&packet=", 1)

class TestHoppieApiConnectMethodParams(unittest.TestCase):
    _URL: str = 'http://example.com/1'

    @responses.activate
    def test_connect_get_peek(self):
        expected_from = 'CALLSIGN'
        msg = PeekMessage(expected_from)
        expected_params = msg.get_msg_params()
        expected_params.pop('packet')
        expected_logon = '1234abcd'

        responses.get(self._URL, body='ok', match=[
            matchers.query_param_matcher({'logon': expected_logon, **expected_params})
        ])

        actual = HoppieAPI(expected_logon, self._URL).connect(msg)

        self.assertIsInstance(actual, SuccessResponse)

    @responses.activate
    def test_connect_get_poll(self):
        expected_from = 'CALLSIGN'
        msg = PollMessage(expected_from)
        expected_params = msg.get_msg_params()
        expected_params.pop('packet')
        expected_logon = '1234abcd'

        responses.get(self._URL, body='ok', match=[
            matchers.query_param_matcher({'logon': expected_logon, **expected_params})
        ])

        actual = HoppieAPI(expected_logon, self._URL).connect(msg)

        self.assertIsInstance(actual, SuccessResponse)

    @responses.activate
    def test_connect_post_telex(self):
        expected_from = 'CALLSIGN'
        expected_to = 'OPS'
        expected_message = 'MESSAGE'
        msg = TelexMessage(expected_from, expected_to, expected_message)
        expected_params = msg.get_msg_params()
        expected_data = expected_params.pop('packet')
        expected_logon = '1234abcd'

        responses.post(self._URL, body='ok', match=[
            matchers.query_param_matcher({'logon': expected_logon, **expected_params}),
            matchers.urlencoded_params_matcher({'packet': expected_data})
        ])

        actual = HoppieAPI(expected_logon, self._URL).connect(msg)

        self.assertIsInstance(actual, SuccessResponse)

class TestHoppieApiConnectValid(unittest.TestCase):
    _URL: str = 'http://example.com/1'

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

class TestHoppieApiConnectInvalid(unittest.TestCase):
    _URL: str = 'http://example.com/1'

    @responses.activate
    def test_malformed_error_reason(self):
        responses.get(self._URL, body='error {malformed')

        self.assertRaises(ValueError, lambda: HoppieAPI('', self._URL).connect(PeekMessage('CALLSIGN')))

    @responses.activate
    def test_malformed_status_code(self):
        responses.get(self._URL, body='invalid')

        self.assertRaises(ValueError, lambda: HoppieAPI('', self._URL).connect(PeekMessage('CALLSIGN')))

    @responses.activate
    def test_http_redirect(self):
        redirect_target = 'http://example.com/2'
        responses.get(self._URL, status=301, headers={'Location': redirect_target})
        responses.get(redirect_target, body='ok')

        actual = HoppieAPI('', self._URL).connect(PeekMessage('CALLSIGN'))

        self.assertIsInstance(actual, SuccessResponse)

    @responses.activate
    def test_http_error_400(self):
        responses.get(self._URL, status=400)

        self.assertRaises(ConnectionError, lambda: HoppieAPI('', self._URL).connect(PeekMessage('CALLSIGN')))

    @responses.activate
    def test_http_error_500(self):
        responses.get(self._URL, status=500)

        self.assertRaises(ConnectionError, lambda: HoppieAPI('', self._URL).connect(PeekMessage('CALLSIGN')))