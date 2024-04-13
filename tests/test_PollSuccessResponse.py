from hoppie_connector.Responses import PollSuccessResponse, HoppieResponse, SuccessResponse as Super
import unittest

class TestPollSuccessResponse(unittest.TestCase):
    def test_get_code(self):
        expected = HoppieResponse.ResponseCode.OK
        actual = PollSuccessResponse([]).get_code()
        self.assertEqual(expected, actual)

    def test_compare_same(self):
        value1 = PollSuccessResponse([])
        value2 = value1
        self.assertEqual(value1, value2)

    def test_str(self):
        expected = '''[OK] []'''
        actual = str(PollSuccessResponse([]))
        self.assertEqual(expected, actual)

    def test_repr(self):
        expected = PollSuccessResponse([])
        actual = eval(repr(expected))
        self.assertEqual(expected, actual)

    def test_hierarchy_super(self):
        self.assertIsInstance(PollSuccessResponse([]), Super)