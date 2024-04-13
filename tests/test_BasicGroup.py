from hoppie_connector.ADSC import BasicGroup
from datetime import datetime, UTC
import unittest

class TestBasicGroupComparison(unittest.TestCase):
    def test_same(self):
        value1 = BasicGroup(
            timestamp=datetime(year=2000, month=1, day=1, hour=18, minute=20, tzinfo=UTC),
            position=(10.0, -10.0),
            altitude=3000
        )
        value2 = value1
        self.assertEqual(value1, value2)

    def test_equal_content(self):
        value1 = BasicGroup(
            timestamp=datetime(year=2000, month=1, day=1, hour=18, minute=20, tzinfo=UTC),
            position=(10.0, -10.0),
            altitude=3000
        )
        value2 = BasicGroup(
            timestamp=datetime(year=2000, month=1, day=1, hour=18, minute=20, tzinfo=UTC),
            position=(10.0, -10.0),
            altitude=3000
        )
        self.assertEqual(value1, value2)

    def test_ignore_datetime_parts(self):
        value1 = BasicGroup(
            timestamp=datetime(year=1999, month=2, day=1, hour=18, minute=20, second=10, tzinfo=UTC),
            position=(10.0, -10.0),
            altitude=3000
        )
        value2 = BasicGroup(
            timestamp=datetime(year=2000, month=1, day=1, hour=18, minute=20, second=0, tzinfo=UTC),
            position=(10.0, -10.0),
            altitude=3000
        )
        self.assertEqual(value1, value2)

    def test_differing(self):
        value1 = BasicGroup(
            timestamp=datetime(year=2000, month=1, day=1, hour=18, minute=20, tzinfo=UTC),
            position=(10.0, -10.0),
            altitude=3000
        )
        value2 = BasicGroup(
            timestamp=datetime(year=2000, month=1, day=2, hour=19, minute=10, tzinfo=UTC),
            position=(12.0, -12.0),
            altitude=1000
        )
        self.assertNotEqual(value1, value2)