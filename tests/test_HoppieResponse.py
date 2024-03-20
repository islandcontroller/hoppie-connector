from hoppie_connector.Responses import HoppieResponse
import unittest

class TestValidHoppieResponse(unittest.TestCase):
    def test_get_code(self):
        expected = HoppieResponse.ResponseCode.OK
        actual = HoppieResponse(expected).get_code()
        self.assertEqual(expected, actual)

    def test_compare_same(self):
        value1 = HoppieResponse(HoppieResponse.ResponseCode.OK)
        value2 = value1
        self.assertEqual(value1, value2)

    def test_compare_equal_content(self):
        value1 = HoppieResponse(HoppieResponse.ResponseCode.OK)
        value2 = HoppieResponse(HoppieResponse.ResponseCode.OK)
        self.assertEqual(value1, value2)

    def test_compare_differing(self):
        value1 = HoppieResponse(HoppieResponse.ResponseCode.OK)
        value2 = HoppieResponse(HoppieResponse.ResponseCode.ERROR)
        self.assertNotEqual(value1, value2)

    def test_str(self):
        expected = '[ERROR]'
        actual = str(HoppieResponse(HoppieResponse.ResponseCode.ERROR))
        self.assertEqual(expected, actual)

    def test_code_repr(self):
        expected = HoppieResponse.ResponseCode.ERROR
        actual = eval(repr(expected))
        self.assertEqual(expected, actual)

    def test_response_repr(self):
        expected = HoppieResponse(HoppieResponse.ResponseCode.OK)
        actual = eval(repr(expected))
        self.assertEqual(expected, actual)

class TestHoppieResponseInputValidation(unittest.TestCase):
    def test_invalid_code_type(self):
        self.assertRaises(ValueError, lambda: HoppieResponse('invalid'))
