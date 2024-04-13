from hoppie_connector.Responses import ErrorResponse, HoppieResponse, HoppieResponse as Super
import unittest

class TestErrorResponse(unittest.TestCase):
    def test_get_code(self):
        expected = HoppieResponse.ResponseCode.ERROR
        actual = ErrorResponse('').get_code()
        self.assertEqual(expected, actual)

    def test_get_reason(self):
        expected = 'reason'
        actual = ErrorResponse(expected).get_reason()
        self.assertEqual(expected, actual)

    def test_compare_same(self):
        value1 = ErrorResponse('reason')
        value2 = value1
        self.assertEqual(value1, value2)

    def test_compare_equal_content(self):
        value1 = ErrorResponse('reason')
        value2 = ErrorResponse('reason')
        self.assertEqual(value1, value2)

    def test_compare_differing(self):
        value1 = ErrorResponse('reason1')
        value2 = ErrorResponse('reason2')
        self.assertNotEqual(value1, value2)

    def test_str(self):
        expected = '[ERROR] reason'
        actual = str(ErrorResponse('reason'))
        self.assertEqual(expected, actual)

    def test_repr(self):
        expected = ErrorResponse('reason')
        actual = eval(repr(expected))
        self.assertEqual(expected, actual)

    def test_hierarchy_super(self):
        self.assertIsInstance(ErrorResponse(''), Super)