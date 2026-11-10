"""Behavior tests with isolated command stubs; no target mutations or registry calls."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'audit.sh'


def report(total=0):
    return json.dumps({'metadata': {'vulnerabilities': {
        'info': 0, 'low': 0, 'moderate': 0, 'high': total,
        'critical': 0, 'total': total,
    }}})


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bin = self.root / 'bin'
        self.bin.mkdir()
        self.app = self.root / 'app with spaces'
        self.app.mkdir()
        (self.app / 'package-lock.json').write_text('{}')
        for name in ('apt-get', 'apt-mark', 'systemctl', 'ss', 'docker'):
            self.stub(name, 'exit 0\n')
        self.stub('npm', 'echo called >> "$NPM_CALLS"\n'
                  'printf "%s" "$AUDIT_JSON"\nexit "${AUDIT_RC:-0}"\n')
        self.env = dict(os.environ, PATH=f'{self.bin}:' + os.environ['PATH'],
                        NPM_CALLS=str(self.root / 'calls'), AUDIT_JSON=report())

    def stub(self, name, body):
        file = self.bin / name
        file.write_text('#!/usr/bin/env bash\n' + body)
        file.chmod(0o755)

    def run_audit(self, *args):
        return subprocess.run(['bash', str(SCRIPT), *args], env=self.env,
                              text=True, capture_output=True, timeout=20)

    def test_default_does_not_call_npm(self):
        result = self.run_audit('--app-root', str(self.app))
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('requires --network-scans', result.stdout)
        self.assertFalse((self.root / 'calls').exists())

    def test_valid_clean_scan(self):
        result = self.run_audit('--app-root', str(self.app), '--network-scans')
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('SCANNED: npm runtime dependency findings', result.stdout)
        self.assertIn('total=0', result.stdout)

    def test_findings_are_not_collector_failure(self):
        self.env.update(AUDIT_JSON=report(2), AUDIT_RC='1')
        result = self.run_audit('--app-root', str(self.app), '--network-scans')
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('high=2', result.stdout)

    def test_registry_error_is_unknown(self):
        self.env.update(AUDIT_JSON='{"error":{"code":"E401"}}', AUDIT_RC='1')
        result = self.run_audit('--app-root', str(self.app), '--network-scans')
        self.assertEqual(result.returncode, 1)
        self.assertIn('UNKNOWN: npm audit result unusable', result.stdout)
        self.assertNotIn('total=0', result.stdout)

    def test_invalid_and_incomplete_json_are_unknown(self):
        for output in ('not json', '{}', '{"metadata":{"vulnerabilities":null}}'):
            with self.subTest(output=output):
                self.env['AUDIT_JSON'] = output
                result = self.run_audit('--app-root', str(self.app), '--network-scans')
                self.assertEqual(result.returncode, 1)
                self.assertNotIn('SCANNED: npm runtime', result.stdout)

    def test_unexpected_exit_status_is_unknown(self):
        self.env['AUDIT_RC'] = '2'
        result = self.run_audit('--app-root', str(self.app), '--network-scans')
        self.assertEqual(result.returncode, 1)
        self.assertIn('UNKNOWN: npm audit', result.stdout)

    def test_wrong_json_container_types_are_explicitly_unknown(self):
        for value in ([], '', 1, None, True):
            for result_json in ({'metadata': value},
                                {'metadata': {'vulnerabilities': value}}):
                with self.subTest(result_json=result_json):
                    self.env['AUDIT_JSON'] = json.dumps(result_json)
                    result = self.run_audit('--app-root', str(self.app), '--network-scans')
                    self.assertEqual(result.returncode, 1)
                    self.assertIn('UNKNOWN: npm audit result unusable', result.stdout)
                    self.assertNotIn('Traceback', result.stdout + result.stderr)

    def test_bad_severity_values_are_unknown(self):
        for value in (-1, True, '0', 0.5, None):
            with self.subTest(value=value):
                output = json.loads(report())
                output['metadata']['vulnerabilities']['high'] = value
                self.env['AUDIT_JSON'] = json.dumps(output)
                result = self.run_audit('--app-root', str(self.app), '--network-scans')
                self.assertEqual(result.returncode, 1)
                self.assertIn('UNKNOWN: npm audit result unusable', result.stdout)

    def test_docker_access_failure_is_unknown(self):
        self.stub('docker', 'echo "permission denied" >&2\nexit 1\n')
        result = self.run_audit()
        self.assertEqual(result.returncode, 1)
        self.assertIn('UNKNOWN: command failed (exit 1): docker', result.stdout)

    def test_apt_simulation_runs_once(self):
        self.stub('apt-get', 'echo called >> "$APT_CALLS"\necho "Inst example [1] (2 local)"\n')
        self.env['APT_CALLS'] = str(self.root / 'apt-calls')
        result = self.run_audit()
        self.assertEqual(result.returncode, 0)
        self.assertEqual((self.root / 'apt-calls').read_text().splitlines(), ['called'])
        self.assertIn('Simulated package installations: 1', result.stdout)

    def test_later_success_does_not_hide_failed_root(self):
        result = self.run_audit('--app-root', str(self.root / 'missing'),
                                '--app-root', str(self.app), '--network-scans')
        self.assertEqual(result.returncode, 1)
        self.assertIn('SCANNED: npm runtime', result.stdout)
        self.assertIn('INCOMPLETE:', result.stdout)

    def test_inconsistent_counts_or_success_status_are_unknown(self):
        for output in (report(1), report().replace('"total": 0', '"total": 3')):
            with self.subTest(output=output):
                self.env['AUDIT_JSON'] = output
                result = self.run_audit('--app-root', str(self.app), '--network-scans')
                self.assertEqual(result.returncode, 1)

    def test_systemd_failure_is_not_zero_failed_units(self):
        self.stub('systemctl', 'echo "no bus" >&2\nexit 1\n')
        result = self.run_audit()
        self.assertEqual(result.returncode, 1)
        self.assertIn('UNKNOWN: command failed', result.stdout)
        self.assertIn('no bus', result.stdout)

    def test_apt_failure_is_not_zero_updates(self):
        self.stub('apt-get', 'echo "bad indexes" >&2\nexit 100\n')
        result = self.run_audit()
        self.assertEqual(result.returncode, 1)
        self.assertIn('UNKNOWN: APT simulation failed', result.stdout)
        self.assertNotIn('Simulated package installations:', result.stdout)

    def test_invalid_options(self):
        for args in (('--app-root',), ('--app-root', '--network-scans'), ('--bad',)):
            with self.subTest(args=args):
                self.assertEqual(self.run_audit(*args).returncode, 2)

    def test_missing_app_root(self):
        result = self.run_audit('--app-root', str(self.root / 'missing'))
        self.assertEqual(result.returncode, 1)
        self.assertIn('application directory unavailable', result.stdout)

    def test_help(self):
        result = self.run_audit('--help')
        self.assertEqual(result.returncode, 0)
        self.assertIn('Usage:', result.stdout)


if __name__ == '__main__':
    unittest.main()
