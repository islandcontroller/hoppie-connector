from hoppie_connector.Responses import PeekSuccessResponse, HoppieResponse, SuccessResponse as Super
import unittest

class TestPeekSuccessResponse(unittest.TestCase):
    def test_get_code(self):
        expected = HoppieResponse.ResponseCode.OK
        actual = PeekSuccessResponse([]).get_code()
        self.assertEqual(expected, actual)

    def test_compare_same(self):
        value1 = PeekSuccessResponse([])
        value2 = value1
        self.assertEqual(value1, value2)

    def test_str(self):
        expected = '''[OK] []'''
        actual = str(PeekSuccessResponse([]))
        self.assertEqual(expected, actual)

    def test_repr(self):
        expected = PeekSuccessResponse([])
        actual = eval(repr(expected))
        self.assertEqual(expected, actual)

    def test_hierarchy_super(self):
        self.assertIsInstance(PeekSuccessResponse([]), Super)