import unittest

from sadp_operations import normalize_mac, parse_command_response, validate_network_settings

MAC = 'aa:bb:cc:dd:ee:ff'


def reply(result='0', operation='update', mac=MAC):
    return (f'<ProbeMatch><MAC>{mac}</MAC><Types>{operation}</Types>'
            f'<Result>{result}</Result></ProbeMatch>')


class AcknowledgementTests(unittest.TestCase):
    def test_explicit_success_in_helper_output(self):
        for result in ('0', 'success', 'SUCCESS'):
            with self.subTest(result=result):
                output = "Sending 'update' command...\nResponse:\n---\n" + reply(result) + '\n---'
                self.assertTrue(parse_command_response(output, expected_mac=MAC)[0])

    def test_unknown_errors_echoes_and_other_devices_never_succeed(self):
        cases = [
            '', 'permission denied', "Error: ezvizunbind: password error",
            'unsuccessful', 'success', '<Probe><Types>update</Types><Result>0</Result></Probe>',
            reply('4'), reply('failed'), reply('pwerror'), '<ProbeMatch><Result>0',
            reply(operation='inquiry'), reply(mac='00:11:22:33:44:55'),
            '<ProbeMatch><Result>0</Result></ProbeMatch>',
        ]
        for text in cases:
            with self.subTest(text=text):
                self.assertFalse(parse_command_response(text, expected_mac=MAC)[0])

    def test_nonzero_exit_overrides_success_xml(self):
        self.assertEqual(parse_command_response(reply(), 1, expected_mac=MAC), (False, 'command_failed'))

    def test_unbind_is_operation_specific(self):
        self.assertTrue(parse_command_response(reply(operation='ezvizUnbind'), 0, 'ezvizunbind', MAC)[0])
        self.assertFalse(parse_command_response(reply(), 0, 'ezvizunbind', MAC)[0])

    def test_xml_namespaces_and_mac_formats(self):
        xml = reply(mac='AA-BB-CC-DD-EE-FF').replace('<ProbeMatch>', '<ProbeMatch xmlns="urn:sadp">')
        self.assertTrue(parse_command_response(xml, expected_mac=MAC)[0])

    def test_password_error_overrides_success(self):
        xml = reply().replace('<Result>', '<PWError>true</PWError><Result>')
        self.assertEqual(parse_command_response(xml, expected_mac=MAC), (False, 'command_password_error'))


class ValidationTests(unittest.TestCase):
    def validate(self, ip='192.168.1.64', mask='255.255.255.0', gateway='192.168.1.1', port='8000', dhcp=False):
        return validate_network_settings(ip, mask, gateway, port, dhcp)

    def test_valid_static_and_dhcp_settings(self):
        self.assertIsNone(self.validate())
        self.assertIsNone(self.validate(gateway=''))
        self.assertIsNone(self.validate(gateway='0.0.0.0'))
        self.assertIsNone(self.validate(ip='', mask='', gateway='', dhcp=True))

    def test_rejects_bad_addresses(self):
        for ip in ('999.999.999.999', 'a.b.c.d', '127.0.0.1', '0.0.0.0', '239.1.1.1', '192.168.1.0', '192.168.1.255'):
            with self.subTest(ip=ip):
                self.assertEqual(self.validate(ip=ip), 'invalid_ip_msg')

    def test_requires_contiguous_dotted_netmask(self):
        for mask in ('255.0.255.0', '24', '0.0.0.255', 'a.b.c.d'):
            with self.subTest(mask=mask):
                self.assertEqual(self.validate(mask=mask), 'invalid_subnet_msg')

    def test_gateway_must_be_a_different_host_in_subnet(self):
        for gateway in ('garbage', '192.168.2.1', '192.168.1.64', '192.168.1.0', '192.168.1.255'):
            with self.subTest(gateway=gateway):
                self.assertEqual(self.validate(gateway=gateway), 'invalid_gateway_msg')

    def test_port_validation_also_applies_to_dhcp(self):
        for port in ('0', '65536', '-1', 'abc', '8.0', '８０００', ''):
            with self.subTest(port=port):
                self.assertEqual(self.validate(port=port, dhcp=True), 'invalid_port_msg')
        self.assertIsNone(self.validate(port='65535'))

    def test_mac_validation(self):
        self.assertEqual(normalize_mac('AA-BB-CC-DD-EE-FF'), 'aabbccddeeff')
        for mac in ('', 'invalid', 'AA:BB:CC', 'zz:bb:cc:dd:ee:ff'):
            self.assertEqual(normalize_mac(mac), '')
