import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))


class HRMSSmokeTest(unittest.TestCase):
    def test_shared_validation_and_catalog_shape(self):
        from domain.shared import normalize_payload, require_fields
        from domain.registry import resource_catalog

        require_fields({"name": "Ana"}, ("name",))
        self.assertEqual(normalize_payload({"name": "Ana", "empty": None}), {"name": "Ana"})
        catalog = resource_catalog()
        self.assertEqual(len(catalog), 12)
        self.assertTrue(sum(item["count"] for item in catalog) >= 1000)


if __name__ == "__main__":
    unittest.main()
