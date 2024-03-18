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
    _EXPECTED_LOGON: str = '1234abcd'
    
    def setUp(self) -> None:
        super().setUp()
        self._UUT = HoppieAPI(self._EXPECTED_LOGON, self._URL)
    
    def trigger_connect(self, msg):
        return self._UUT.connect(msg)

    @responses.activate
    def test_connect_get_peek(self):
        expected_from = 'CALLSIGN'
        msg = PeekMessage(expected_from)
        expected_params = msg.get_msg_params()
        expected_params.pop('packet')

        responses.get(self._URL, body='ok', match=[
            matchers.query_param_matcher({'logon': self._EXPECTED_LOGON, **expected_params})
        ])

        actual = self.trigger_connect(msg)

        self.assertIsInstance(actual, SuccessResponse)

    @responses.activate
    def test_connect_get_poll(self):
        expected_from = 'CALLSIGN'
        msg = PollMessage(expected_from)
        expected_params = msg.get_msg_params()
        expected_params.pop('packet')

        responses.get(self._URL, body='ok', match=[
            matchers.query_param_matcher({'logon': self._EXPECTED_LOGON, **expected_params})
        ])

        actual = self.trigger_connect(msg)

        self.assertIsInstance(actual, SuccessResponse)

    @responses.activate
    def test_connect_post_telex(self):
        expected_from = 'CALLSIGN'
        expected_to = 'OPS'
        expected_message = 'MESSAGE'
        msg = TelexMessage(expected_from, expected_to, expected_message)
        expected_params = msg.get_msg_params()
        expected_data = expected_params.pop('packet')

        responses.post(self._URL, body='ok', match=[
            matchers.query_param_matcher({'logon': self._EXPECTED_LOGON, **expected_params}),
            matchers.urlencoded_params_matcher({'packet': expected_data})
        ])

        actual = self.trigger_connect(msg)

        self.assertIsInstance(actual, SuccessResponse)

class TestHoppieApiConnectValid(unittest.TestCase):
    _URL: str = 'http://example.com/1'

    def setUp(self) -> None:
        super().setUp()
        self._UUT = HoppieAPI('', self._URL)
        self._peek = PeekMessage('CALLSIGN')
        self._poll = PollMessage('CALLSIGN')
    
    def trigger_connect(self, type):
        match type:
            case 'peek': return self._UUT.connect(self._peek)
            case 'poll': return self._UUT.connect(self._poll)

    @responses.activate
    def test_error_illegal_logon_code(self):
        responses.get(self._URL, body='error {illegal logon code}')

        actual: ErrorResponse = self.trigger_connect('peek')
        
        self.assertIsInstance(actual, ErrorResponse)
        self.assertEqual('illegal logon code', actual.get_reason())

    @responses.activate
    def test_success_empty(self):
        responses.get(self._URL, body='ok')

        actual: SuccessResponse = self.trigger_connect('peek')
        
        self.assertIsInstance(actual, SuccessResponse)
        self.assertListEqual([], actual.get_items())

    @responses.activate
    def test_success_poll(self):
        responses.get(self._URL, body='ok {OPS telex {MESSAGE 1}} {OPS telex {MESSAGE 2}}')
        expected_items = [
            {'id': None, 'from': 'OPS', 'type': 'telex', 'packet': 'MESSAGE 1'},
            {'id': None, 'from': 'OPS', 'type': 'telex', 'packet': 'MESSAGE 2'}
        ]

        actual: SuccessResponse = self.trigger_connect('poll')
        
        self.assertIsInstance(actual, SuccessResponse)
        self.assertListEqual(expected_items, actual.get_items())

    @responses.activate
    def test_success_peek(self):
        responses.get(self._URL, body='ok {1 OPS telex {MESSAGE 1}} {2 OPS telex {MESSAGE 2}}')
        expected_items = [
            {'id': 1, 'from': 'OPS', 'type': 'telex', 'packet': 'MESSAGE 1'},
            {'id': 2, 'from': 'OPS', 'type': 'telex', 'packet': 'MESSAGE 2'}
        ]

        actual: SuccessResponse = self.trigger_connect('peek')
        
        self.assertIsInstance(actual, SuccessResponse)
        self.assertListEqual(expected_items, actual.get_items())

class TestHoppieApiConnectInvalid(unittest.TestCase):
    _URL: str = 'http://example.com/1'

    def setUp(self) -> None:
        super().setUp()
        self._UUT = HoppieAPI('', self._URL)
        self._msg = PeekMessage('CALLSIGN')

    def trigger_connect(self):
        return self._UUT.connect(self._msg)

    @responses.activate
    def test_malformed_error_reason(self):
        responses.get(self._URL, body='error {malformed')

        self.assertRaises(ValueError, self.trigger_connect)

    @responses.activate
    def test_malformed_status_code(self):
        responses.get(self._URL, body='invalid')

        self.assertRaises(ValueError, self.trigger_connect)

    @responses.activate
    def test_http_redirect(self):
        redirect_target = 'http://example.com/2'
        responses.get(self._URL, status=301, headers={'Location': redirect_target})
        responses.get(redirect_target, body='ok')

        actual = self.trigger_connect()

        self.assertIsInstance(actual, SuccessResponse)

    @responses.activate
    def test_http_error_400(self):
        responses.get(self._URL, status=400)

        self.assertRaises(ConnectionError, self.trigger_connect)

    @responses.activate
    def test_http_error_500(self):
        responses.get(self._URL, status=500)

        self.assertRaises(ConnectionError, self.trigger_connect)

    @responses.activate
    def test_http_nonascii_content(self):
        responses.get(self._URL, body=b'\x12\x39\x0a\xf9')

        self.assertRaises(UnicodeDecodeError, self.trigger_connect)