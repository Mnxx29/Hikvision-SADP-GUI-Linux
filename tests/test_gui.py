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

from gui_sadp import SADPGui, ModifyThread, UnbindThread, ScanThread, APP_ID
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

    def test_incremental_results_show_and_filter_before_scan_finishes(self):
        second = dict(DEVICE, ip='192.168.1.65', mac='aa:bb:cc:dd:ee:00')
        self.window.txt_filter.setText('192.168.1.64')
        self.window.mostrar_dispositivos([dict(DEVICE), second])
        self.assertEqual(self.window.tabla.rowCount(), 2)
        self.assertEqual(len(self.window.dispositivos), 2)
        self.assertIn('2', self.window.lbl_count.text())
        visible_ips = [self.window.tabla.item(row, 1).text()
                       for row in range(self.window.tabla.rowCount())
                       if not self.window.tabla.isRowHidden(row)]
        self.assertEqual(visible_ips, [DEVICE['ip']])

    def test_double_click_ip_opens_default_browser_without_prompt(self):
        with patch('gui_sadp.webbrowser.open', return_value=True) as browser, \
                patch('gui_sadp.QMessageBox.question') as question:
            self.window.doble_clic_celda(0, 1)
            self.window.doble_clic_celda(0, 2)
            browser.assert_called_once_with('http://192.168.1.64')
            question.assert_not_called()

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

    def test_language_menu_switches_and_persists_full_language_names(self):
        for lang, label in (('es', 'Español'), ('en', 'English')):
            action = self.window.language_actions[lang]
            self.assertEqual(action.text(), label)
            action.trigger()
            self.assertEqual(self.window.current_lang, lang)
            self.assertEqual(self.window.settings.value('appLanguage'), lang)
            self.assertTrue(action.isChecked())
            self.assertEqual(self.window.language_menu.title(), 'Idioma' if lang == 'es' else 'Language')
        self.assertIs(self.window.btn_settings.menu(), self.window.settings_menu)

    def test_desktop_identity_matches_installed_launcher(self):
        self.assertEqual(self.app.desktopFileName(), APP_ID)
        self.assertEqual(self.app.applicationName(), APP_ID)
        self.assertFalse(self.app.windowIcon().isNull())
        self.assertFalse(self.window.windowIcon().isNull())
        desktop = pathlib.Path(__file__).resolve().parents[1] / 'packaging' / 'sadp-gui.desktop'
        self.assertEqual(desktop.stem, APP_ID)
        self.assertIn('StartupWMClass=' + APP_ID, desktop.read_text())

    def test_buttons_fit_both_languages_and_table_can_scroll_beside_panel(self):
        self.window.show()
        self.window.resize(960, 600)
        self.window.panel_modificar.show()
        for lang in ('en', 'es'):
            self.window.cambiar_idioma(lang)
            self.app.processEvents()
            for button in (self.window.btn_scan, self.window.btn_export,
                           self.window.btn_unbind, self.window.btn_toggle_panel):
                self.assertGreaterEqual(button.width(), button.sizeHint().width(), button.text())
        self.assertFalse(self.window.tabla.wordWrap())
        self.assertGreaterEqual(self.window.tabla.columnWidth(2), 148)
        self.assertGreater(self.window.tabla.horizontalScrollBar().maximum(), 0)

    def test_icon_has_transparent_exterior_and_opaque_artwork(self):
        from PyQt6.QtGui import QImage
        assets = pathlib.Path(__file__).resolve().parents[1] / 'assets'
        for filename in ('hikvision-sadp.png', 'hikvision-sadp-128.png', 'hikvision-sadp-256.png'):
            image = QImage(str(assets / filename))
            self.assertFalse(image.isNull())
            self.assertTrue(image.hasAlphaChannel())
            self.assertEqual(image.pixelColor(0, 0).alpha(), 0)
            self.assertGreaterEqual(image.pixelColor(image.width() // 2, image.height() // 2).alpha(), 250)


class WorkerTests(unittest.TestCase):
    def test_worker_emits_each_device_before_final_list(self):
        worker = ScanThread()
        events = []
        worker.device_found.connect(lambda device: events.append(('found', device['mac'])))
        worker.devices.connect(lambda devices: events.append(('complete', len(devices))))
        def discover(*, timeout, debug, on_device):
            on_device(dict(DEVICE))
            self.assertEqual(events, [('found', DEVICE['mac'])])
            return [dict(DEVICE)]
        with patch('sadp_discover.discover', side_effect=discover):
            worker.run()
        self.assertEqual(events, [('found', DEVICE['mac']), ('complete', 1)])

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
