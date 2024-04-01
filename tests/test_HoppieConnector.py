from hoppie_connector import HoppieConnector, HoppieError, HoppieWarning
from hoppie_connector.Messages import TelexMessage
from responses import matchers
import responses
import unittest

class TestHoppieConnectorSuccess(unittest.TestCase):
    _URL = 'http://example.com/api'
    _LOGON = 'logon'
    _STATION = 'STATION'

    @responses.activate
    def test_peek(self):
        responses.get(self._URL, body='ok {1 CALLSIGN telex {MESSAGE}}', match=[
            matchers.query_param_matcher({'logon': self._LOGON, 'from': self._STATION, 'to': 'SERVER', 'type': 'peek'})
        ])

        expected = [(1, TelexMessage('CALLSIGN', self._STATION, 'MESSAGE'))]
        actual = HoppieConnector(self._STATION, self._LOGON, self._URL).peek()
        self.assertListEqual(expected, actual)

    @responses.activate
    def test_poll(self):
        responses.get(self._URL, body='ok {CALLSIGN telex {MESSAGE}}', match=[
            matchers.query_param_matcher({'logon': self._LOGON, 'from': self._STATION, 'to': 'SERVER', 'type': 'poll'})
        ])
        
        expected = expected = [TelexMessage('CALLSIGN', self._STATION, 'MESSAGE')]
        actual = HoppieConnector(self._STATION, self._LOGON, self._URL).poll()
        self.assertEqual(expected, actual)

    @responses.activate
    def test_send_telex(self):
        callsign = 'CALLSIGN'
        message = 'MESSAGE'
        responses.post(self._URL, body='ok', match=[
            matchers.query_param_matcher({'logon': self._LOGON, 'from': self._STATION, 'to': callsign, 'type': 'telex'}),
            matchers.urlencoded_params_matcher({'packet': message})
        ])
        HoppieConnector(self._STATION, self._LOGON, self._URL).send_telex(callsign, message)

class TestHoppieConnectorErrorHandling(unittest.TestCase):
    _URL = 'http://example.com/api'
    _LOGON = 'logon'
    _STATION = 'STATION'

    @responses.activate
    def test_error(self):
        responses.post(self._URL, body='error {illegal logon code}')
        self.assertRaises(HoppieError, lambda: HoppieConnector(self._STATION, self._LOGON, self._URL).send_telex('CALLSIGN', 'MESSAGE'))

    @responses.activate
    def test_peek_warning(self):
        responses.get(self._URL, body='ok {1 CALLSIGN unknown {OTHER DATA}}')
        self.assertWarns(HoppieWarning, lambda: HoppieConnector(self._STATION, self._LOGON, self._URL).peek())

    @responses.activate
    def test_poll_warning(self):
        responses.get(self._URL, body='ok {CALLSIGN unknown {OTHER DATA}}')
        self.assertWarns(HoppieWarning, lambda: HoppieConnector(self._STATION, self._LOGON, self._URL).poll())