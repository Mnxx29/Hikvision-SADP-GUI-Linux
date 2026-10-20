import csv
import os
import pathlib
import subprocess
import tempfile
import unittest
from unittest.mock import patch

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QSettings, Qt
except ImportError:
    raise unittest.SkipTest('PyQt6 is required for the desktop tests')

from gui_sadp import SADPGui, ModifyThread, UnbindThread, ScanThread
from i18n import TRANSLATIONS

DEVICE = {'ip': '192.168.1.64', 'mac': 'aa:bb:cc:dd:ee:ff', 'nombre': 'Camera',
          'tipo': '141938', 'serial': 'DS-TEST-123', 'estado': 'Active', 'puerto': '8000',
          'http_port': '80', 'subnet': '255.255.255.0', 'gateway': '192.168.1.1', 'dhcp': 'true'}


class GuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.settings_dir = tempfile.TemporaryDirectory()
        QSettings.setDefaultFormat(QSettings.Format.IniFormat)
        QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.UserScope, cls.settings_dir.name)
        cls.app = QApplication.instance() or QApplication([])

    @classmethod
    def tearDownClass(cls):
        cls.settings_dir.cleanup()

    def setUp(self):
        self.window = SADPGui()
        self.window.mostrar_dispositivos([dict(DEVICE)])
        self.window.seleccionar_fila(0, 1)

    def tearDown(self):
        self.window.close()

    def test_unsupported_fields_remain_disabled_in_both_languages(self):
        for lang in ('en', 'es'):
            self.window.current_lang = lang
            self.window.retranslate_ui()
            self.window.seleccionar_fila(0, 1)
            for name in ('txt_http_port', 'txt_ipv6', 'txt_ipv6_gw', 'txt_ipv6_prefix', 'chk_hik'):
                self.assertFalse(getattr(self.window, name).isEnabled(), name)
            self.assertTrue(self.window.txt_port.isReadOnly())

    def test_dhcp_selection_keeps_static_fields_disabled(self):
        for name in ('txt_ip', 'txt_subnet', 'txt_gateway'):
            self.assertFalse(getattr(self.window, name).isEnabled(), name)
        self.window.chk_dhcp.setChecked(False)
        self.assertTrue(self.window.txt_ip.isEnabled())

    def test_discovered_identity_cannot_be_edited(self):
        self.assertFalse(self.window.tabla.item(0, 1).flags() & Qt.ItemFlag.ItemIsEditable)
        self.assertFalse(self.window.tabla.item(0, 2).flags() & Qt.ItemFlag.ItemIsEditable)
        self.assertTrue(self.window.tabla.item(0, 3).flags() & Qt.ItemFlag.ItemIsEditable)

    def test_csv_keeps_serial_and_quotes_user_model(self):
        with tempfile.TemporaryDirectory() as folder:
            target = str(pathlib.Path(folder) / 'devices.csv')
            self.window.guardar_modelo_panel('Camera, "Entrance"')
            with patch('gui_sadp.QFileDialog.getSaveFileName', return_value=(target, '')), \
                    patch('gui_sadp.QMessageBox.information'):
                self.window.exportar_csv()
            with open(target, newline='', encoding='utf-8') as stream:
                row = next(csv.DictReader(stream))
            self.assertEqual(row['serial'], DEVICE['serial'])
            self.assertEqual(row['modelo'], 'Camera, "Entrance"')

    def test_invalid_port_does_not_start_network_operation(self):
        self.window.txt_sdk_port.setText('65536')
        self.window.txt_password.setText('fake')
        with patch('gui_sadp.QMessageBox.warning') as warning, patch('gui_sadp.ModifyThread') as thread:
            self.window.ejecutar_modificacion()
            warning.assert_called_once()
            thread.assert_not_called()

    def test_translation_keys_match(self):
        self.assertEqual(set(TRANSLATIONS['en']), set(TRANSLATIONS['es']))


class WorkerTests(unittest.TestCase):
    def test_empty_native_scan_does_not_fall_back_or_report_an_error(self):
        worker = ScanThread()
        devices, errors = [], []
        worker.devices.connect(devices.append)
        worker.error.connect(errors.append)
        with patch('sadp_discover.discover', return_value=[]), patch.object(worker, '_fallback') as fallback:
            worker.run()
        fallback.assert_not_called()
        self.assertEqual(devices, [[]])
        self.assertEqual(errors, [])

    def test_fallback_uses_xml_file_and_preserves_full_serial(self):
        worker = ScanThread()
        xml = '<SADPDeviceList><ProbeMatch><MAC>aa:bb:cc:dd:ee:ff</MAC><IPv4Address>192.168.1.64</IPv4Address><DeviceSN>DS-FULL-SERIAL-123456789</DeviceSN></ProbeMatch></SADPDeviceList>'
        def helper(cmd, **kwargs):
            pathlib.Path(cmd[cmd.index('--output') + 1]).write_text(xml)
            return subprocess.CompletedProcess(cmd, 0, 'progress logs', '')
        with patch('gui_sadp.obtener_binario_path', return_value='fake'), patch('gui_sadp.subprocess.run', side_effect=helper):
            devices = worker._fallback()
        self.assertEqual(devices[0]['serial'], 'DS-FULL-SERIAL-123456789')

    def test_modify_error_is_not_retried_or_reported_successful(self):
        worker = ModifyThread('fake', '192.168.1.64', DEVICE['mac'], 'secret',
                              '192.168.1.65', '255.255.255.0', '', '8000', False)
        results = []
        worker.result.connect(lambda *args: results.append(args))
        with patch('gui_sadp.subprocess.run', return_value=subprocess.CompletedProcess([], 1, '', 'permission denied')) as run:
            worker.run()
            run.assert_called_once()
        self.assertFalse(results[0][0])
        self.assertEqual(worker.password, '')

    def test_unbind_error_containing_command_name_never_succeeds(self):
        worker = UnbindThread('fake', '192.168.1.64', DEVICE['mac'], 'secret')
        results = []
        worker.result.connect(lambda *args: results.append(args))
        with patch('gui_sadp.subprocess.run', return_value=subprocess.CompletedProcess([], 1, '', 'Error: ezvizunbind: password error')):
            worker.run()
        self.assertFalse(results[0][0])
        self.assertNotIn('secret', results[0][1])

    def test_timeout_is_unconfirmed_without_resend(self):
        worker = UnbindThread('fake', '', DEVICE['mac'], 'secret')
        results = []
        worker.result.connect(lambda *args: results.append(args))
        with patch('gui_sadp.subprocess.run', side_effect=subprocess.TimeoutExpired('fake', 15)) as run:
            worker.run()
            run.assert_called_once()
        self.assertFalse(results[0][0])

    def test_success_requires_device_ack_and_password_is_xml_escaped(self):
        worker = UnbindThread('fake', '', DEVICE['mac'], 'p<&')
        results = []
        worker.result.connect(lambda *args: results.append(args))
        ack = '<ProbeMatch><MAC>aa:bb:cc:dd:ee:ff</MAC><Types>ezvizUnbind</Types><Result>0</Result></ProbeMatch>'
        with patch('gui_sadp.subprocess.run', return_value=subprocess.CompletedProcess([], 0, ack, '')) as run:
            worker.run()
            self.assertIn('p&lt;&amp;', run.call_args.args[0])
        self.assertTrue(results[0][0])
