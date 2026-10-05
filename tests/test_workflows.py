import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))


class WorkflowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from db import initialize
        from domain.services import seed_demo

        initialize()
        seed_demo()

    def test_payroll_run_aggregates_active_employees(self):
        from domain.services import run_payroll

        result = run_payroll("2030-01", 100)
        self.assertEqual(result["run"]["status"], "processed")
        self.assertGreater(result["employee_count"], 0)
        self.assertAlmostEqual(result["run"]["net"], sum(item["net"] for item in result["items"]))

    def test_generic_crud_validates_and_audits_a_module_resource(self):
        from domain.store import archive_record, audit_events, create_record, update_record

        created = create_record("performance", "objective", {"employee_id": 1, "cycle": "2030-Q1", "score": 0})
        self.assertEqual(created["module"], "performance")
        updated = update_record("performance", "objective", created["id"], {"score": 92})
        self.assertEqual(updated["payload"]["score"], 92)
        archived = archive_record("performance", "objective", created["id"])
        self.assertEqual(archived["status"], "archived")
        self.assertGreaterEqual(len(audit_events(10)), 3)

    def test_openapi_exposes_core_contract(self):
        from api_schema import openapi_schema

        schema = openapi_schema()
        self.assertEqual(schema["openapi"], "3.0.3")
        self.assertIn("/api/records/{module}/{resource}", schema["paths"])
        self.assertEqual(len(schema["x-modules"]), 12)

    def test_each_module_exposes_a_validated_resource(self):
        from domain.registry import load_resource, resource_catalog
        from domain.store import create_record

        for module in resource_catalog():
            resource = module["resources"][0]
            definition = load_resource(module["key"], resource)
            value = 1 if definition.FIELDS[0].endswith("_id") else "test"
            record = create_record(module["key"], resource, {definition.FIELDS[0]: value})
            self.assertEqual(record["module"], module["key"])


if __name__ == "__main__":
    unittest.main()
