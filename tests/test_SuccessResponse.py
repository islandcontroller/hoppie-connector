from hoppie_connector.Responses import SuccessResponse, HoppieResponse
import unittest

class TestErrorResponse(unittest.TestCase):
    def test_get_code(self):
        expected = HoppieResponse.ResponseCode.OK
        actual = SuccessResponse([]).get_code()
        self.assertEqual(expected, actual)

    def test_get_items(self):
        expected = [{'id': 1, 'from': 'FROM', 'type': 'type', 'packet': ''}]
        actual = SuccessResponse(expected).get_items()
        self.assertEqual(expected, actual)

    def test_compare_same(self):
        value1 = SuccessResponse([])
        value2 = value1
        self.assertEqual(value1, value2)

    def test_compare_equal_content(self):
        value1 = SuccessResponse([])
        value2 = SuccessResponse([])
        self.assertEqual(value1, value2)

    def test_compare_differing(self):
        value1 = SuccessResponse([])
        value2 = SuccessResponse([{'id': 1, 'from': 'FROM', 'type': 'type', 'packet': ''}])
        self.assertNotEqual(value1, value2)

    def test_str(self):
        expected = '''[OK] [{'id': 1, 'from': 'FROM', 'type': 'type', 'packet': ''}]'''
        actual = str(SuccessResponse([{'id': 1, 'from': 'FROM', 'type': 'type', 'packet': ''}]))
        self.assertEqual(expected, actual)

    def test_repr(self):
        expected = SuccessResponse([{'id': 1, 'from': 'FROM', 'type': 'type', 'packet': ''}])
        actual = eval(repr(expected))
        self.assertEqual(expected, actual)
