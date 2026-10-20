#!/bin/bash
# Read-only configuration inspection plus discovery. No firewall/routing changes.
set -u
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
printf 'SADP diagnostics — %s\n' "$(date -Is)"
python3 --version
ip -4 -o addr show scope global
ip route show
for key in net.ipv4.conf.all.rp_filter net.ipv4.conf.default.rp_filter; do sysctl "$key"; done
ss -uln | grep -E '37020|State' || true
if command -v ufw >/dev/null; then
    sudo -n ufw status verbose || echo 'For firewall details run: sudo ufw status verbose'
fi
if [ -f /etc/sudoers.d/sadp-gui-routing ]; then
    echo 'WARNING: legacy 1.0.2 sudoers file still exists; upgrade to 1.0.3.'
fi
if [ -f /opt/hikvision-sadp/sadp_discover.py ]; then
    python3 /opt/hikvision-sadp/sadp_discover.py --timeout 6 --debug
elif [ -f "$ROOT_DIR/sadp_discover.py" ]; then
    python3 "$ROOT_DIR/sadp_discover.py" --timeout 6 --debug
fi
