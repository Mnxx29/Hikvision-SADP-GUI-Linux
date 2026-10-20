"""Validation and acknowledgement parsing, independent of Qt and the network."""

import ipaddress
import re
import xml.etree.ElementTree as ET

CSV_FIELDS = (
    'ip', 'mac', 'modelo', 'tipo', 'estado', 'puerto', 'http_port',
    'serial', 'version', 'subnet', 'gateway', 'dhcp',
)


def normalize_mac(value):
    compact = value.replace(':', '').replace('-', '').lower()
    return compact if re.fullmatch(r'[0-9a-f]{12}', compact) else ''


def validate_network_settings(ip, mask, gateway, port, dhcp=False):
    """Return a translation key for the first invalid field, or None."""
    if not port.isascii() or not port.isdecimal() or not 1 <= int(port) <= 65535:
        return 'invalid_port_msg'
    if dhcp:
        return None
    try:
        address = ipaddress.IPv4Address(ip)
        if address.is_unspecified or address.is_loopback or address.is_multicast:
            return 'invalid_ip_msg'
    except ipaddress.AddressValueError:
        return 'invalid_ip_msg'
    try:
        ipaddress.IPv4Address(mask)
        network = ipaddress.IPv4Network(f'{ip}/{mask}', strict=False)
        if str(network.netmask) != mask:
            return 'invalid_subnet_msg'
    except (ipaddress.AddressValueError, ipaddress.NetmaskValueError):
        return 'invalid_subnet_msg'
    if address == ipaddress.IPv4Address('255.255.255.255') or (
        network.prefixlen < 31 and address in (network.network_address, network.broadcast_address)
    ):
        return 'invalid_ip_msg'
    if gateway and gateway != '0.0.0.0':
        try:
            router = ipaddress.IPv4Address(gateway)
            if (router not in network or router == address or router.is_loopback
                    or router.is_multicast or router.is_unspecified
                    or (network.prefixlen < 31 and router in
                        (network.network_address, network.broadcast_address))):
                return 'invalid_gateway_msg'
        except ipaddress.AddressValueError:
            return 'invalid_gateway_msg'
    return None


def parse_command_response(text, returncode=0, operation='update', expected_mac=''):
    """Require an explicit device acknowledgement; never trust CLI logs or echoes.

    The pinned helper prints a 'Response:' section around the raw XML reply.
    Only ProbeMatch replies count. Unknown firmware result codes fail closed.
    No raw response is returned, because it may contain credentials.
    """
    if returncode != 0:
        return False, 'command_failed'
    if not text.strip():
        return False, 'command_no_response'
    start = re.search(r'<(?:[\w.-]+:)?ProbeMatch\b', text)
    if not start:
        return False, 'command_unconfirmed'
    fragment = text[start.start():].rstrip('\x00 \r\n')
    end = re.search(r'</(?:[\w.-]+:)?ProbeMatch\s*>', fragment)
    if not end:
        return False, 'command_unconfirmed'
    try:
        root = ET.fromstring(fragment[:end.end()])
    except ET.ParseError:
        return False, 'command_unconfirmed'
    fields = {el.tag.rsplit('}', 1)[-1].lower(): (el.text or '').strip().lower()
              for el in root}
    if expected_mac and normalize_mac(fields.get('mac', '')) != normalize_mac(expected_mac):
        return False, 'command_unconfirmed'
    if fields.get('types', '').lower() not in ('', operation.lower()):
        return False, 'command_unconfirmed'
    result = fields.get('result', '')
    if result in ('pwerror', 'passworderror', 'errorpassword') or fields.get('pwerror') in ('true', '1'):
        return False, 'command_password_error'
    if result in ('0', 'success'):
        return True, 'command_confirmed'
    return False, 'command_rejected' if result else 'command_unconfirmed'


def parse_update_response(text, returncode=0, expected_mac=''):
    return parse_command_response(text, returncode, 'update', expected_mac)
