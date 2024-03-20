from hoppie_connector.API import HoppieAPI
from hoppie_connector.Messages import HoppieMessage, PeekMessage, PollMessage, TelexMessage
from responses import matchers
import responses
import unittest

class TestHoppieApiURL(unittest.TestCase):
    @responses.activate
    def test_default_url(self):
        expected_url = 'https://www.hoppie.nl/acars/system/connect.html'
        responses.get(expected_url, body='ok')
        HoppieAPI('').connect(PeekMessage('CALLSIGN'))

    @responses.activate
    def test_custom_url(self):
        expected_url = 'https://www.example.com/1'
        responses.get(expected_url, body='ok')
        HoppieAPI('', expected_url).connect(PeekMessage('CALLSIGN'))

class TestHoppieApiConnectMethodParams(unittest.TestCase):
    _URL: str = 'http://example.com/1'
    _EXPECTED_LOGON: str = '1234abcd'
    
    def setUp(self) -> None:
        super().setUp()
        self._UUT = HoppieAPI(self._EXPECTED_LOGON, self._URL)
        self._peek = PeekMessage('CALLSIGN')
        self._poll = PollMessage('CALLSIGN')
        self._telex = TelexMessage('CALLSIGN', 'OPS', 'MESSAGE')
    
    def _trigger_connect(self, msg):
        return self._UUT.connect(msg)
    
    def _get_expected_get_params(self, msg: HoppieMessage):
        p = msg.get_msg_params()
        if not p['packet']: p.pop('packet')
        return {'logon': self._EXPECTED_LOGON, **p}
    
    def _get_expected_post_params(self, msg: HoppieMessage):
        p = msg.get_msg_params()
        p.pop('packet')
        return {'logon': self._EXPECTED_LOGON, **p}
    
    def _get_expected_post_data(self, msg: HoppieMessage):
        p = msg.get_msg_params()
        return {'packet': p['packet']}

    @responses.activate
    def test_connect_get_peek(self):
        responses.get(self._URL, body='ok', match=[
            matchers.query_param_matcher(self._get_expected_get_params(self._peek))
        ])
        self._trigger_connect(self._peek)

    @responses.activate
    def test_connect_get_poll(self):
        responses.get(self._URL, body='ok', match=[
            matchers.query_param_matcher(self._get_expected_get_params(self._poll))
        ])
        self._trigger_connect(self._poll)

    @responses.activate
    def test_connect_post_telex(self):
        responses.post(self._URL, body='ok', match=[
            matchers.query_param_matcher(self._get_expected_post_params(self._telex)),
            matchers.urlencoded_params_matcher(self._get_expected_post_data(self._telex))
        ])
        self._trigger_connect(self._telex)

class TestHoppieApiConnectErrorHandling(unittest.TestCase):
    _URL: str = 'http://example.com/1'

    def setUp(self) -> None:
        super().setUp()
        self._UUT = HoppieAPI('', self._URL)
        self._msg = PeekMessage('CALLSIGN')

    def _trigger_connect(self):
        return self._UUT.connect(self._msg)

    @responses.activate
    def test_http_redirect(self):
        redirect_target = 'http://example.com/2'
        responses.get(self._URL, status=301, headers={'Location': redirect_target})
        responses.get(redirect_target, body='ok')
        self._trigger_connect()

    @responses.activate
    def test_http_error_400(self):
        responses.get(self._URL, status=400)
        self.assertRaises(ConnectionError, self._trigger_connect)

    @responses.activate
    def test_http_error_500(self):
        responses.get(self._URL, status=500)
        self.assertRaises(ConnectionError, self._trigger_connect)

    @responses.activate
    def test_http_nonascii_content(self):
        responses.get(self._URL, body=b'\x12\x39\x0a\xf9')
        self.assertRaises(UnicodeDecodeError, self._trigger_connect)

    def test_invalid_connect_msg(self):
        self.assertRaises(ValueError, lambda: self._UUT.connect(None))

class TestHoppieApiComparison(unittest.TestCase):
    def test_same(self):
        value1 = HoppieAPI('logon')
        value2 = value1
        self.assertEqual(value1, value2)

    def test_equal_content(self):
        value1 = HoppieAPI('logon', 'url')
        value2 = HoppieAPI('logon', 'url')
        self.assertEqual(value1, value2)

    def test_differing_logon(self):
        value1 = HoppieAPI('logon1', 'url')
        value2 = HoppieAPI('logon2', 'url')
        self.assertNotEqual(value1, value2)

    def test_differing_url(self):
        value1 = HoppieAPI('logon', 'url1')
        value2 = HoppieAPI('logon', 'url2')
        self.assertNotEqual(value1, value2)

class TestHoppieApiRepresentation(unittest.TestCase):
    def test_repr(self):
        expected = HoppieAPI('logon', 'url')
        actual = eval(repr(expected))
        self.assertEqual(expected, actual)