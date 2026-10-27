import unittest
from unittest.mock import patch

from sadp_discover import build_probe, parse_response, discover
import xml.etree.ElementTree as ET

ADDRESS = ('192.168.10.156', 37020)
PACKET = b'<ProbeMatch><MAC>aa-bb-cc-dd-ee-ff</MAC><IPv4Address>192.168.10.156</IPv4Address><Activated>false</Activated><DeviceSN>DS-TEST</DeviceSN></ProbeMatch>'


class DiscoveryTests(unittest.TestCase):
    def test_probe_is_valid_inquiry_xml(self):
        root = ET.fromstring(build_probe())
        self.assertEqual(root.findtext('Types'), 'inquiry')
        self.assertTrue(root.findtext('Uuid'))

    def test_response_and_binary_prefix(self):
        for packet in (PACKET, b'\x01\x00' + PACKET + b'\x00\x00'):
            with self.subTest(packet=packet):
                device = parse_response(packet, ADDRESS)
                self.assertEqual(device['ip'], ADDRESS[0])
                self.assertEqual(device['estado'], 'Inactive')
                self.assertEqual(device['serial'], 'DS-TEST')

    def test_namespace_and_case_variations(self):
        packet = PACKET.replace(b'<ProbeMatch>', b'<ProbeMatch xmlns="urn:sadp">').replace(b'MAC>', b'mac>')
        self.assertEqual(parse_response(packet, ADDRESS)['serial'], 'DS-TEST')

    def test_discards_malformed_xml_missing_mac_and_probe_echoes(self):
        for packet in (b'garbage', b'<ProbeMatch>', b'<ProbeMatch><MAC>invalid</MAC></ProbeMatch>',
                       b'<ProbeMatch><IPv4Address>1.2.3.4</IPv4Address></ProbeMatch>',
                       PACKET.replace(b'ProbeMatch', b'Probe')):
            self.assertIsNone(parse_response(packet, ADDRESS))

    def test_duplicate_mac_formats_produce_one_device(self):
        packets = iter([(PACKET, ADDRESS), (PACKET.replace(b'aa-bb-cc-dd-ee-ff', b'AA:BB:CC:DD:EE:FF'), ADDRESS)])
        clock = iter([0, 0, 0, .1, .2, .3, 2])
        arrivals = []
        with patch('sadp_discover.socket.socket') as factory, \
                patch('sadp_discover.get_interface_ips', return_value=['192.168.10.178']), \
                patch('sadp_discover.get_broadcast_addrs', return_value=[]), \
                patch('sadp_discover.time.monotonic', side_effect=lambda: next(clock)), \
                patch('sadp_discover.select.select', side_effect=lambda *args: ([factory.return_value], [], [])):
            factory.return_value.__enter__.return_value = factory.return_value
            factory.return_value.recvfrom.side_effect = lambda *args: next(packets)
            self.assertEqual(len(discover(timeout=1, on_device=arrivals.append)), 1)
            self.assertEqual([device['ip'] for device in arrivals], [ADDRESS[0]])
            factory.return_value.__exit__.assert_called_once()
