import json
import shlex
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import network_setup as setup


class FakeNetwork:
    def __init__(self, active=True):
        self.active = active
        self.values = dict.fromkeys(setup.KEYS, '1')
        self.rules = []
        self.calls = []

    def __call__(self, *args):
        self.calls.append(args)
        if args[:2] == ('sysctl', '-n'):
            return self.values[args[2]]
        if args[:2] == ('sysctl', '-p'):
            self.values = dict.fromkeys(setup.KEYS, '2')
        elif args[:2] == ('sysctl', '-w'):
            key, value = args[2].split('=')
            self.values[key] = value
        elif args == ('ufw', 'status'):
            return 'Status: active' if self.active else 'Status: inactive'
        elif args == ('ufw', 'show', 'added'):
            return '\n'.join('ufw ' + shlex.join(rule) for rule in self.rules)
        elif args[:2] == ('ufw', 'allow'):
            rule = list(args[1:])
            if rule not in self.rules:
                self.rules.append(rule)
        elif args[:3] == ('ufw', '--force', 'delete'):
            self.rules.remove(list(args[3:]))
        return ''


class NetworkSetupTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        root = Path(self.folder.name)
        self.patches = [patch.object(setup, 'STATE', root / 'state/network-state.json'),
                        patch.object(setup, 'CONF', root / 'sysctl.conf'),
                        patch.object(setup, 'LEGACY_SUDOERS', root / 'legacy-sudoers'),
                        patch.object(setup.shutil, 'which', return_value='/usr/sbin/ufw')]
        for p in self.patches:
            p.start()
        self.network = FakeNetwork()
        self.run_patch = patch.object(setup, 'run', side_effect=self.network)
        self.run_patch.start()

    def tearDown(self):
        self.run_patch.stop()
        for p in reversed(self.patches):
            p.stop()
        self.folder.cleanup()

    def test_upgrade_removes_legacy_privileges_and_preserves_original_state(self):
        setup.LEGACY_SUDOERS.write_text('unsafe legacy configuration')
        setup.configure()
        first = setup.STATE.read_text()
        setup.configure()
        self.assertFalse(setup.LEGACY_SUDOERS.exists())
        self.assertEqual(setup.STATE.read_text(), first)
        setup.remove()
        self.assertEqual(self.network.values, dict.fromkeys(setup.KEYS, '1'))
        self.assertFalse(setup.CONF.exists())
        self.assertFalse(setup.STATE.exists())

    def test_existing_firewall_rules_survive_removal(self):
        original = list(setup.RULES[0])
        self.network.rules.append(original)
        setup.configure()
        setup.remove()
        self.assertEqual(self.network.rules, [original])

    def test_existing_administrator_shorthand_is_not_relabelled_or_deleted(self):
        original = ['allow', '37020/udp']
        self.network.rules.append(original)
        setup.configure()
        self.assertEqual(json.loads(setup.STATE.read_text())['ufw_rules'], [])
        setup.remove()
        self.assertEqual(self.network.rules, [original])
        self.assertFalse(any(cmd[:2] == ('ufw', 'allow') for cmd in self.network.calls))

    def test_inactive_firewall_is_never_enabled_or_modified(self):
        self.network.active = False
        setup.configure()
        setup.remove()
        self.assertFalse(self.network.rules)
        self.assertFalse(any('enable' in cmd or 'allow' in cmd for cmd in self.network.calls))

    def test_user_changes_to_runtime_value_are_preserved(self):
        setup.configure()
        self.network.values[setup.KEYS[0]] = '0'
        setup.remove()
        self.assertEqual(self.network.values[setup.KEYS[0]], '0')
        self.assertEqual(self.network.values[setup.KEYS[1]], '1')

    def test_modified_config_is_not_overwritten_or_removed(self):
        setup.configure()
        setup.CONF.write_text('# administrator settings\n')
        with self.assertRaises(RuntimeError):
            setup.configure()
        setup.remove()
        self.assertEqual(setup.CONF.read_text(), '# administrator settings\n')

    def test_install_without_ufw(self):
        with patch.object(setup.shutil, 'which', return_value=None):
            setup.configure()
            setup.remove()
        self.assertFalse(any(cmd[0] == 'ufw' for cmd in self.network.calls))
