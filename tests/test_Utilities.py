from hoppie_connector.Utilities import is_valid_airport_code, is_valid_station_name, get_fixed_width_float_str
import unittest

class TestIsValidStationNameUtility(unittest.TestCase):
    def test_valid(self):
        self.assertTrue(is_valid_station_name('STATION'))
        
    def test_invalid_empty(self):
        self.assertFalse(is_valid_station_name(''))

    def test_invalid_too_long(self):
        self.assertFalse(is_valid_station_name('123456789'))

    def test_invalid_lowercase(self):
        self.assertFalse(is_valid_station_name('ops'))

    def test_invalid_char(self):
        self.assertFalse(is_valid_station_name('D-ABCD'))

class TestIsValidAirportCodeUtility(unittest.TestCase):
    def test_valid(self):
        self.assertTrue(is_valid_airport_code('ZZZZ'))

    def test_invalid_too_short(self):
        self.assertFalse(is_valid_airport_code('LAX'))

    def test_invalid_too_long(self):
        self.assertFalse(is_valid_airport_code('ABCDE'))

    def test_invalid_char(self):
        self.assertFalse(is_valid_airport_code('AB01'))

class TestFixedWidthFloatStrUtility(unittest.TestCase):
    def test_1(self):
        self.assertEqual('1.000000', get_fixed_width_float_str(1.0, 8))

    def test_neg1(self):
        self.assertEqual('-1.00000', get_fixed_width_float_str(-1.0, 8))

    def test_10(self):
        self.assertEqual('10.00000', get_fixed_width_float_str(10.0, 8))

    def test_overflow(self):
        self.assertEqual('1000.0', get_fixed_width_float_str(1000, 3))