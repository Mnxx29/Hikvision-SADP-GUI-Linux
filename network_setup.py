#!/usr/bin/env python3
"""Fixed network settings, called as root by installers; no NOPASSWD helper.

State survives upgrades. Settings and firewall rules that predate installation
are kept. prerm calls remove before dpkg removes this module.
"""
import json
import os
from pathlib import Path
import shutil
import shlex
import subprocess
import sys

STATE = Path('/var/lib/hikvision-sadp/network-state.json')
CONF = Path('/etc/sysctl.d/60-hikvision-sadp.conf')
LEGACY_SUDOERS = Path('/etc/sudoers.d/sadp-gui-routing')
KEYS = ('net.ipv4.conf.all.rp_filter', 'net.ipv4.conf.default.rp_filter')
CONFIG = '# Managed by hikvision-sadp-gui\n' + ''.join(f'{key}=2\n' for key in KEYS)
RULES = (
    ['allow', 'in', 'proto', 'udp', 'to', 'any', 'port', '37020', 'comment', 'hikvision-sadp-gui'],
    # The pinned Go helper receives replies on ephemeral source ports.
    ['allow', 'in', 'proto', 'udp', 'from', 'any', 'port', '37020', 'comment', 'hikvision-sadp-gui'],
    ['allow', 'out', 'proto', 'udp', 'to', '239.255.255.250', 'port', '37020', 'comment', 'hikvision-sadp-gui'],
)
ENV = {'PATH': '/usr/sbin:/usr/bin:/sbin:/bin', 'LC_ALL': 'C'}


def run(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True,
                          timeout=30, env=ENV).stdout.strip()


def save(state):
    STATE.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    temporary = STATE.with_suffix('.tmp')
    temporary.write_text(json.dumps(state, indent=2) + '\n')
    temporary.chmod(0o600)
    temporary.replace(STATE)


def configure():
    LEGACY_SUDOERS.unlink(missing_ok=True)
    if CONF.exists() and CONF.read_text() != CONFIG:
        raise RuntimeError(f'{CONF} has administrator changes; refusing to overwrite it')
    if STATE.exists():
        state = json.loads(STATE.read_text())
    else:
        state = {'rp_filter': {key: run('sysctl', '-n', key) for key in KEYS}, 'ufw_rules': []}
        save(state)
    CONF.write_text(CONFIG)
    CONF.chmod(0o644)
    run('sysctl', '-p', str(CONF))
    # Never enable UFW. 1.0.2 did not track ownership of its firewall rules,
    # so those legacy rules cannot safely be removed automatically on upgrade.
    if shutil.which('ufw', path=ENV['PATH']) and run('ufw', 'status').startswith('Status: active'):
        # UFW can update an existing rule's comment instead of adding a rule.
        # Do not claim/delete an administrator's existing SADP policy, even when
        # its spelling is different (e.g. "allow 37020/udp").
        existing = run('ufw', 'show', 'added')
        for line in existing.splitlines():
            tokens = shlex.split(line)
            if ('hikvision-sadp-gui' not in tokens and any(
                    token == '37020' or token.startswith('37020/') for token in tokens)):
                print('Keeping existing SADP firewall policy; review it with ufw show added.', file=sys.stderr)
                return
        for rule in RULES:
            before = run('ufw', 'show', 'added')
            run('ufw', *rule)
            if run('ufw', 'show', 'added') != before and rule not in state['ufw_rules']:
                state['ufw_rules'].append(rule)
                save(state)


def remove():
    LEGACY_SUDOERS.unlink(missing_ok=True)
    if not STATE.exists():
        return
    state = json.loads(STATE.read_text())
    if shutil.which('ufw', path=ENV['PATH']):
        for rule in state.get('ufw_rules', []):
            run('ufw', '--force', 'delete', *rule)
    if CONF.exists() and CONF.read_text() == CONFIG:
        CONF.unlink()
        for key, original in state['rp_filter'].items():
            if key in KEYS and original in ('0', '1', '2') and run('sysctl', '-n', key) == '2':
                run('sysctl', '-w', f'{key}={original}')
    elif CONF.exists():
        print(f'Keeping administrator-modified {CONF}', file=sys.stderr)
    STATE.unlink()
    try:
        STATE.parent.rmdir()
    except OSError:
        pass


def main():
    if os.geteuid() != 0:
        raise SystemExit('Run this installer helper as root (sudo).')
    if sys.argv[1:] == ['configure']:
        configure()
    elif sys.argv[1:] == ['remove']:
        remove()
    else:
        raise SystemExit('Usage: network_setup.py configure|remove')


if __name__ == '__main__':
    main()
