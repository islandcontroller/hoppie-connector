from hoppie_connector.Responses import SuccessResponse, HoppieResponse, HoppieResponse as Super
import unittest

class TestSuccessResponse(unittest.TestCase):
    def test_get_code(self):
        expected = HoppieResponse.ResponseCode.OK
        actual = SuccessResponse().get_code()
        self.assertEqual(expected, actual)

    def test_compare_same(self):
        value1 = SuccessResponse()
        value2 = value1
        self.assertEqual(value1, value2)

    def test_str(self):
        expected = '''[OK]'''
        actual = str(SuccessResponse())
        self.assertEqual(expected, actual)

    def test_repr(self):
        expected = SuccessResponse()
        actual = eval(repr(expected))
        self.assertEqual(expected, actual)

    def test_hierarchy_super(self):
        self.assertIsInstance(SuccessResponse(), Super)