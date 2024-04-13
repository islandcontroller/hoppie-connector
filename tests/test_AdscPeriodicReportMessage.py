from hoppie_connector.Messages import AdscPeriodicReportMessage, AdscMessage, AdscMessage as Super
from hoppie_connector.ADSC import AdscData, BasicGroup, FlightIdentGroup, EarthRefGroup, MeteoGroup
import datetime
import unittest

class TestAdscPeriodicReportMessage(unittest.TestCase):
    _EXPECTED_DATA: AdscData = AdscData(
        basic=BasicGroup(datetime.datetime(2000, 1, 1, 18, 20, tzinfo=datetime.UTC), (-10.0, 10.0), 3000),
        flight_ident=FlightIdentGroup('CALLSIGN')
    )
    _EXPECTED_PACKET: str = 'REPORT CALLSIGN 011820 -10.0000 10.00000 3000'
    
    def setUp(self) -> None:
        super().setUp()
        self._UUT = AdscPeriodicReportMessage('CALLSIGN', 'OPS', self._EXPECTED_DATA)

    def test_get_adsc_msg_type(self):
        self.assertEqual(AdscMessage.AdscMessageType.REPORT_PERIODIC, self._UUT.get_adsc_msg_type())

    def test_get_data(self):
        self.assertEqual(self._EXPECTED_DATA, self._UUT.get_data())

    def test_get_packet_content(self):
        self.assertEqual(self._EXPECTED_PACKET, self._UUT.get_packet_content())

    def test_hierarchy_super(self):
        self.assertIsInstance(self._UUT, Super)

class TestAdscMessageFromPacket(unittest.TestCase):
    def test_basic_ident(self):
        expected = AdscPeriodicReportMessage('CALLSIGN', 'OPS', AdscData(
            basic=BasicGroup(datetime.datetime(2000, 1, 1, 18, 20, tzinfo=datetime.UTC), (-10.0, 10.0), 3000),
            flight_ident=FlightIdentGroup('CALLSIGN')
        ))
        actual = AdscPeriodicReportMessage.from_packet('CALLSIGN', 'OPS', 'REPORT CALLSIGN 011820 -10.0000 10.00000 3000')
        self.assertEqual(expected, actual)

    def test_basic_ident_earthref(self):
        expected = AdscPeriodicReportMessage('CALLSIGN', 'OPS', AdscData(
            basic=BasicGroup(datetime.datetime(2000, 1, 1, 18, 20, tzinfo=datetime.UTC), (-10.0, 10.0), 3000),
            flight_ident=FlightIdentGroup('CALLSIGN'),
            earth_ref=EarthRefGroup(320, 150, None)
        ))
        actual = AdscPeriodicReportMessage.from_packet('CALLSIGN', 'OPS', 'REPORT CALLSIGN 011820 -10.0000 10.00000 3000 320 150')
        self.assertEqual(expected, actual)

    def test_basic_ident_earthref_meteo(self):
        expected = AdscPeriodicReportMessage('CALLSIGN', 'OPS', AdscData(
            basic=BasicGroup(datetime.datetime(2000, 1, 1, 18, 20, tzinfo=datetime.UTC), (-10.0, 10.0), 3000),
            flight_ident=FlightIdentGroup('CALLSIGN'),
            earth_ref=EarthRefGroup(320, 150, None),
            meteo=MeteoGroup((60, 43), -5)
        ))
        actual = AdscPeriodicReportMessage.from_packet('CALLSIGN', 'OPS', 'REPORT CALLSIGN 011820 -10.0000 10.00000 3000 320 150 060/43 -5')
        self.assertEqual(expected, actual)

    def test_basic_ident_earthref_meteo_vrate(self):
        expected = AdscPeriodicReportMessage('CALLSIGN', 'OPS', AdscData(
            basic=BasicGroup(datetime.datetime(2000, 1, 1, 18, 20, tzinfo=datetime.UTC), (-10.0, 10.0), 3000),
            flight_ident=FlightIdentGroup('CALLSIGN'),
            earth_ref=EarthRefGroup(320, 150, EarthRefGroup.VerticalRate.DESCENT),
            meteo=MeteoGroup((60, 43), -5)
        ))
        actual = AdscPeriodicReportMessage.from_packet('CALLSIGN', 'OPS', 'REPORT CALLSIGN 011820 -10.0000 10.00000 3000 320 150 060/43 -5 DES')
        self.assertEqual(expected, actual)
    
    def test_invalid_format(self):
        # BAVirtual Merlin (?) format with malformed timestamp and incorrect altitude
        self.assertRaises(ValueError, lambda: AdscPeriodicReportMessage.from_packet('CALLSIGN', 'OPS', 'REPORT CALLSIGN 1024 -10.0000 10.00000 30'))

class TestAdscPeriodicReportMessageRepresentation(unittest.TestCase):
    def test_repr(self):
        expected = AdscPeriodicReportMessage('CALLSIGN', 'OPS', AdscData(
            basic=BasicGroup(datetime.datetime(2000, 1, 1, 18, 20, tzinfo=datetime.UTC), (-10.0, 10.0), 3000),
            flight_ident=FlightIdentGroup('CALLSIGN')
        ))
        actual = eval(repr(expected))
        self.assertEqual(expected, actual)

class TestAdscPeriodicReportMessageComparison(unittest.TestCase):
    def test_same(self):
        value1 = AdscPeriodicReportMessage('CALLSIGN', 'OPS', AdscData(
            basic=BasicGroup(datetime.datetime(2000, 1, 1, 18, 20, tzinfo=datetime.UTC), (-10.0, 10.0), 3000),
            flight_ident=FlightIdentGroup('CALLSIGN')
        ))
        value2 = value1
        self.assertEqual(value1, value2)

    def test_equal_content(self):
        value1 = AdscPeriodicReportMessage('CALLSIGN', 'OPS', AdscData(
            basic=BasicGroup(datetime.datetime(2000, 1, 1, 18, 20, tzinfo=datetime.UTC), (-10.0, 10.0), 3000),
            flight_ident=FlightIdentGroup('CALLSIGN')
        ))
        value2 = AdscPeriodicReportMessage('CALLSIGN', 'OPS', AdscData(
            basic=BasicGroup(datetime.datetime(2000, 1, 1, 18, 20, tzinfo=datetime.UTC), (-10.0, 10.0), 3000),
            flight_ident=FlightIdentGroup('CALLSIGN')
        ))
        self.assertEqual(value1, value2)

    def test_differing_data(self):
        value1 = AdscPeriodicReportMessage('CALLSIGN', 'OPS', AdscData(
            basic=BasicGroup(datetime.datetime(2000, 1, 1, 18, 20, tzinfo=datetime.UTC), (-10.0, 10.0), 3000),
            flight_ident=FlightIdentGroup('CALLSIGN')
        ))
        value2 = AdscPeriodicReportMessage('CALLSIGN', 'OPS', AdscData(
            basic=BasicGroup(datetime.datetime(2000, 1, 1, 18, 20, tzinfo=datetime.UTC), (-10.0, 10.0), 3000),
            flight_ident=FlightIdentGroup('CALLSIGN'),
            meteo=MeteoGroup((120, 10), -5)
        ))
        self.assertNotEqual(value1, value2)