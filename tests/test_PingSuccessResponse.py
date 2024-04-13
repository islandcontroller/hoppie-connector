from hoppie_connector.Responses import PingSuccessResponse, HoppieResponse, SuccessResponse as Super
import unittest

class TestPingSuccessResponse(unittest.TestCase):
    def test_get_code(self):
        expected = HoppieResponse.ResponseCode.OK
        actual = PingSuccessResponse([]).get_code()
        self.assertEqual(expected, actual)

    def test_get_stations(self):
        expected = ['NAME1', 'NAME2']
        actual = PingSuccessResponse(expected).get_stations()
        self.assertListEqual(expected, actual)

    def test_compare_same(self):
        value1 = PingSuccessResponse([])
        value2 = value1
        self.assertEqual(value1, value2)

    def test_compare_equal_type(self):
        value1 = PingSuccessResponse([])
        value2 = PingSuccessResponse([])
        self.assertEqual(value1, value2)

    def test_compare_differing_type(self):
        value1 = PingSuccessResponse([])
        value2 = None
        self.assertNotEqual(value1, value2)

    def test_compare_differing_content(self):
        value1 = PingSuccessResponse(['CALLSIGN'])
        value2 = PingSuccessResponse([])
        self.assertNotEqual(value1, value2)

    def test_str(self):
        expected = '''[OK] []'''
        actual = str(PingSuccessResponse([]))
        self.assertEqual(expected, actual)

    def test_repr(self):
        expected = PingSuccessResponse(['TEST1', 'TEST2'])
        actual = eval(repr(expected))
        self.assertEqual(expected, actual)

    def test_hierarchy_super(self):
        self.assertIsInstance(PingSuccessResponse([]), Super)