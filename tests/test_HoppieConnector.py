from hoppie_connector import HoppieConnector, HoppieError, HoppieWarning
from hoppie_connector.Messages import TelexMessage
from hoppie_connector.Responses import PingSuccessResponse
from hoppie_connector.ADSC import AdscData, BasicGroup, FlightIdentGroup
from hoppie_connector.CPDLC import CpdlcResponseRequirement
from responses import matchers
from datetime import timedelta, time, datetime
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

        expected_msg = [(1, TelexMessage('CALLSIGN', self._STATION, 'MESSAGE'))]
        actual_msg, actual_delay = HoppieConnector(self._STATION, self._LOGON, self._URL).peek()
        self.assertListEqual(expected_msg, actual_msg)
        self.assertGreater(actual_delay, timedelta(0))

    @responses.activate
    def test_poll(self):
        responses.get(self._URL, body='ok {CALLSIGN telex {MESSAGE}}', match=[
            matchers.query_param_matcher({'logon': self._LOGON, 'from': self._STATION, 'to': 'SERVER', 'type': 'poll'})
        ])
        
        expected_msg = [TelexMessage('CALLSIGN', self._STATION, 'MESSAGE')]
        actual_msg, actual_delay = HoppieConnector(self._STATION, self._LOGON, self._URL).poll()
        self.assertListEqual(expected_msg, actual_msg)
        self.assertGreater(actual_delay, timedelta(0))

    @responses.activate
    def test_ping(self):
        responses.get(self._URL, body='ok {CALLSIGN}', match=[
            matchers.query_param_matcher({'logon': self._LOGON, 'from': self._STATION, 'to': 'SERVER', 'type': 'ping', 'packet': 'ALL-CALLSIGNS'})
        ])

        expected_msg = ['CALLSIGN']
        actual_msg, actual_delay = HoppieConnector(self._STATION, self._LOGON, self._URL).ping('*')
        self.assertListEqual(expected_msg, actual_msg)
        self.assertGreater(actual_delay, timedelta(0))

    @responses.activate
    def test_send_telex(self):
        callsign = 'CALLSIGN'
        message = 'MESSAGE'
        responses.post(self._URL, body='ok', match=[
            matchers.query_param_matcher({'logon': self._LOGON, 'from': self._STATION, 'to': callsign, 'type': 'telex'}),
            matchers.urlencoded_params_matcher({'packet': message})
        ])
        actual = HoppieConnector(self._STATION, self._LOGON, self._URL).send_telex(callsign, message)
        self.assertGreater(actual, timedelta(0))

    @responses.activate
    def test_send_progress(self):
        responses.get(self._URL, body='ok', match=[
            matchers.query_param_matcher({'logon': self._LOGON, 'from': self._STATION, 'to': 'OPS', 'type': 'progress', 'packet': 'AAAA/BBBB OUT/1820'})
        ])

        actual = HoppieConnector(self._STATION, self._LOGON, self._URL).send_progress('OPS', 'AAAA', 'BBBB', time(hour=18, minute=20))
        self.assertGreater(actual, timedelta(0))

    @responses.activate
    def test_send_adsc_periodic_request(self):
        responses.get(self._URL, body='ok', match=[
            matchers.query_param_matcher({'logon': self._LOGON, 'from': self._STATION, 'to': 'CALLSIGN', 'type': 'ads-c', 'packet': 'REQUEST PERIODIC 120'})
        ])

        actual = HoppieConnector(self._STATION, self._LOGON, self._URL).send_adsc_periodic_request('CALLSIGN', 120)
        self.assertGreater(actual, timedelta(0))

    @responses.activate
    def test_send_adsc_periodic_report(self):
        responses.get(self._URL, body='ok', match=[
            matchers.query_param_matcher({'logon': self._LOGON, 'from': self._STATION, 'to': 'CALLSIGN', 'type': 'ads-c', 'packet': 'REPORT IDENT 011820 10.00000 20.00000 3000'})
        ])

        actual = HoppieConnector(self._STATION, self._LOGON, self._URL).send_adsc_periodic_report('CALLSIGN', data=AdscData(
            basic=BasicGroup(
                timestamp=datetime(year=2000, month=1, day=1, hour=18, minute=20),
                position=(10.0, 20.0),
                altitude=3000.0
            ),
            flight_ident=FlightIdentGroup('IDENT')
        ))
        self.assertGreater(actual, timedelta(0))

    @responses.activate
    def test_send_adsc_cancel(self):
        responses.get(self._URL, body='ok', match=[
            matchers.query_param_matcher({'logon': self._LOGON, 'from': self._STATION, 'to': 'CALLSIGN', 'type': 'ads-c', 'packet': 'REQUEST CANCEL'})
        ])

        actual = HoppieConnector(self._STATION, self._LOGON, self._URL).send_adsc_cancel('CALLSIGN')
        self.assertGreater(actual, timedelta(0))

    @responses.activate
    def test_send_adsc_reject(self):
        responses.get(self._URL, body='ok', match=[
            matchers.query_param_matcher({'logon': self._LOGON, 'from': self._STATION, 'to': 'ATC', 'type': 'ads-c', 'packet': 'REJECT'})
        ])

        actual = HoppieConnector(self._STATION, self._LOGON, self._URL).send_adsc_reject('ATC')
        self.assertGreater(actual, timedelta(0))

    @responses.activate
    def tests_send_cpdlc(self):
        responses.get(self._URL, body='ok', match=[
            matchers.query_param_matcher({'logon': self._LOGON, 'from': self._STATION, 'to': 'ATSU', 'type': 'cpdlc', 'packet': '/data2/1//N/TEST'})
        ])
        
        actual = HoppieConnector(self._STATION, self._LOGON, self._URL).send_cpdlc('ATSU', 1, CpdlcResponseRequirement.N, 'TEST')
        self.assertGreater(actual, timedelta(0))

    @responses.activate
    def test_invalid_connect_type(self):
        responses.post(self._URL, body='ok {1 CALLSIGN telex {MESSAGE}}')

        m = TelexMessage('CALLSIGN', self._STATION, 'MESSAGE')
        cnx = HoppieConnector(self._STATION, self._LOGON, self._URL)
        self.assertRaises(TypeError, lambda: cnx._connect(m, PingSuccessResponse))

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