from hoppie_connector.CPDLC import CpdlcResponseRequirement
import unittest

class TestCpdlcResponseRequirement(unittest.TestCase):
    def test_wilco_unable(self):
        expected = 'WU'
        self.assertEqual(expected, CpdlcResponseRequirement.WILCO_UNABLE)
        self.assertEqual(expected, CpdlcResponseRequirement.W_U)

    def test_affirm_negative(self):
        expected = 'AN'
        self.assertEqual(expected, CpdlcResponseRequirement.AFFIRM_NEGATIVE)
        self.assertEqual(expected, CpdlcResponseRequirement.A_N)

    def test_roger(self):
        expected='R'
        self.assertEqual(expected, CpdlcResponseRequirement.ROGER)
        self.assertEqual(expected, CpdlcResponseRequirement.R)

    def test_not_required(self):
        expected='NE'
        self.assertEqual(expected, CpdlcResponseRequirement.NE)
        self.assertEqual(expected, CpdlcResponseRequirement.NOT_REQUIRED)

    def test_no(self):
        expected='N'
        self.assertEqual(expected, CpdlcResponseRequirement.NO)
        self.assertEqual(expected, CpdlcResponseRequirement.N)

    def test_yes(self):
        expected='Y'
        self.assertEqual(expected, CpdlcResponseRequirement.YES)
        self.assertEqual(expected, CpdlcResponseRequirement.Y)

class TestCpdlcResponseRequirementRepresentation(unittest.TestCase):
    def test_repr(self):
        expected = CpdlcResponseRequirement.WILCO_UNABLE
        actual = eval(repr(expected))
        self.assertEqual(expected, actual)