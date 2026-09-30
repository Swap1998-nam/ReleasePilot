import unittest
from app import assess

GOOD = dict(tests_passed=True, coverage=85, critical_vulnerabilities=0, high_vulnerabilities=0,
            image_signed=True, rollback_ready=True, replicas=2)

class TestAssessment(unittest.TestCase):
    def test_ready(self):
        self.assertEqual(assess(GOOD)['verdict'], 'READY')
    def test_critical_blocks(self):
        self.assertEqual(assess({**GOOD, 'critical_vulnerabilities': 1})['verdict'], 'BLOCKED')
    def test_failed_tests_block(self):
        self.assertEqual(assess({**GOOD, 'tests_passed': False})['verdict'], 'BLOCKED')
    def test_bad_type(self):
        with self.assertRaises(ValueError):
            assess({**GOOD, 'coverage': True})
