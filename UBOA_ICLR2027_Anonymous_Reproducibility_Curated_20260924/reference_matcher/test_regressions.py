import json, unittest
from pathlib import Path
from matcher import match
class DevelopmentRegressionTests(unittest.TestCase):
    def test_recorded_regressions(self):
        for case in json.loads((Path(__file__).parent/"DEVELOPMENT_REGRESSIONS.json").read_text()):
            with self.subTest(case=case["id"]):
                got=match(case["request"],case["evidence"])
                self.assertEqual(got["status"],case["expected_status"])
                self.assertEqual(got["request"],case["request"])
if __name__=="__main__":unittest.main(verbosity=2)
