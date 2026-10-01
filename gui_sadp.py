import sys
import subprocess
import csv
import io
import webbrowser
import os
import shutil
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QMessageBox, QLabel, QProgressBar,
                             QFrame, QScrollArea, QCheckBox, QLineEdit, QFileDialog, QComboBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSettings
from PyQt6.QtGui import QFont

from i18n import t, translate_device_type, traducir_tipo_dispositivo


class SortableItem(QTableWidgetItem):
    """QTableWidgetItem que soporta clave de ordenación personalizada."""
    def __init__(self, text: str, sort_key=None):
        super().__init__(text)
        self.sort_key = sort_key if sort_key is not None else text

    def __lt__(self, other):
        try:
            # Comparar por la clave de ordenación si existe
            return self.sort_key < other.sort_key
        except Exception:
            return super().__lt__(other)


def obtener_binario_path() -> str:
    """Busca el ejecutable SADP en el PATH y en rutas conocidas del sistema."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    binario_path = shutil.which("sadp-linux-amd64") or shutil.which("sadp")
    
    if not binario_path:
        posibles_rutas = [
            os.path.join(script_dir, "sadp-linux-amd64"),
            os.path.join(script_dir, "sadp-linux-amd64-real"),
            os.path.expanduser("~/.local/bin/sadp/sadp-linux-amd64"),
            os.path.expanduser("~/.local/bin/sadp-linux-amd64"),
            "/usr/local/bin/sadp-linux-amd64",
            "./sadp-linux-amd64",
            "./sadp-linux-amd64-real",
            "sadp-windows-amd64.exe",
            "sadp.exe"
        ]
        for ruta in posibles_rutas:
            if os.path.exists(ruta):
                return ruta
    return binario_path or ""


def parse_update_response(response_text: str) -> tuple[bool, str]:
    """Analiza la respuesta enviada por el dispositivo SADP al modificar la red."""
    if not response_text:
        return False, "No se recibió respuesta del dispositivo (timeout de red)."
    
    resp_lower = response_text.lower()
    
    if "pwerror" in resp_lower or "password error" in resp_lower or "errorpassword" in resp_lower or "password is wrong" in resp_lower:
        return False, "Contraseña de administrador incorrecta. Verifica la clave ingresada."
        
    if "failed" in resp_lower or "<result>failed</result>" in resp_lower or "<result>2</result>" in resp_lower:
        return False, f"El dispositivo rechazó la modificación:\n\n{response_text}"
        
    if "success" in resp_lower or "<result>success</result>" in resp_lower or "<result>0</result>" in resp_lower or "types>update" in resp_lower or "probe" in resp_lower:
        return True, "¡Parámetros de red modificados exitosamente!"
        
    return True, f"Respuesta recibida del dispositivo:\n\n{response_text}"


class ModifyThread(QThread):
    """Thread para enviar la orden de modificación de red por SADP sin congelar la GUI"""
    finished = pyqtSignal(bool, str)
    
    def __init__(self, binario_path: str, current_ip: str, mac: str, password: str, 
                 new_ip: str, mask: str, gateway: str, port: str, dhcp: bool):
        super().__init__()
        self.binario_path = binario_path
        self.current_ip = current_ip if current_ip else "0.0.0.0"
        self.mac = mac
        self.password = password
        self.new_ip = new_ip
        self.mask = mask if mask else "255.255.255.0"
        self.gateway = gateway
        self.port = str(port) if port else "8000"
        self.dhcp = "true" if dhcp else "false"

    def run(self):
        try:
            cmd = [
                self.binario_path,
                "send",
                self.current_ip,
                "update",
                "--mac", self.mac,
                "--password", self.password,
                "--ip", self.new_ip,
                "--mask", self.mask,
                "--gateway", self.gateway,
                "--port", self.port,
                f"--dhcp={self.dhcp}"
            ]
            
            resultado = subprocess.run(cmd, capture_output=True, text=True, timeout=15, check=False)
            output = (resultado.stdout + "\n" + resultado.stderr).strip()
            
            # Si el envío a la IP actual falló o hizo timeout, reintentar con 0.0.0.0 (multicast/broadcast por MAC)
            if resultado.returncode != 0 or "timeout" in output.lower() or not output:
                if self.current_ip != "0.0.0.0":
                    cmd[2] = "0.0.0.0"
                    retry_res = subprocess.run(cmd, capture_output=True, text=True, timeout=15, check=False)
                    output = (retry_res.stdout + "\n" + retry_res.stderr).strip()

            success, msg = parse_update_response(output)
            self.finished.emit(success, msg)
        except subprocess.TimeoutExpired:
            self.finished.emit(False, "El dispositivo no respondió a la solicitud de modificación (Timeout).")
        except Exception as e:
            self.finished.emit(False, f"Error al ejecutar comando de modificación: {str(e)}")


class UnbindThread(QThread):
    """Thread para desvincular el dispositivo de Hik-Connect/Ezviz sin congelar la GUI"""
    finished = pyqtSignal(bool, str)
    
    def __init__(self, binario_path: str, current_ip: str, mac: str, password: str):
        super().__init__()
        self.binario_path = binario_path
        self.current_ip = current_ip if current_ip else "0.0.0.0"
        self.mac = mac
        self.password = password

    def run(self):
        try:
            cmd = [
                self.binario_path,
                "send",
                self.current_ip,
                "ezvizunbind",
                "--mac", self.mac,
                "--password", self.password
            ]
            resultado = subprocess.run(cmd, capture_output=True, text=True, timeout=15, check=False)
            output = (resultado.stdout + "\n" + resultado.stderr).strip()
            
            if "success" in output.lower() or "unbind" in output.lower():
                self.finished.emit(True, "Dispositivo desvinculado exitosamente de Hik-Connect/Ezviz.")
            elif "pwerror" in output.lower() or "password" in output.lower():
                self.finished.emit(False, "Contraseña de administrador incorrecta.")
            else:
                self.finished.emit(False, f"Respuesta del dispositivo:\n{output}")
        except subprocess.TimeoutExpired:
            self.finished.emit(False, "El dispositivo no respondió a la solicitud de desvinculación (Timeout).")
        except Exception as e:
            self.finished.emit(False, f"Error al desvincular: {str(e)}")


class ScanThread(QThread):
    """Thread para ejecutar el escaneo sin congelar la interfaz"""
    finished = pyqtSignal()
    error = pyqtSignal(str)
    devices = pyqtSignal(list)
    
    def run(self):
        try:
            # 0. En sistemas Linux, aplicar sysctl para rp_filter (permitir subredes distintas)
            # y habilitar la ruta multicast en TODAS las interfaces de red activas
            if sys.platform.startswith('linux'):
                try:
                    cmd_prep = (
                        "sudo sysctl -w net.ipv4.conf.all.rp_filter=2 >/dev/null 2>&1 || true; "
                        "sudo sysctl -w net.ipv4.conf.default.rp_filter=2 >/dev/null 2>&1 || true; "
                        "for iface in $(ip -o link show | awk -F': ' '$2 !~ /^lo/ && $3 ~ /state (UP|UNKNOWN)/ {print $2}' | cut -d'@' -f1); do "
                        "  [ -z \"$iface\" ] && continue; "
                        "  sudo ip route add 239.255.255.250/32 dev \"$iface\" 2>/dev/null || "
                        "  sudo ip route change 239.255.255.250/32 dev \"$iface\" 2>/dev/null || true; "
                        "done"
                    )
                    subprocess.run(cmd_prep, shell=True, timeout=5)
                except Exception as prep_err:
                    print(f"[DEBUG ScanThread] Aviso preparando interfaces: {prep_err}")

            # ── MÉTODO PRIMARIO: Descubrimiento nativo Python (no depende del binario Go) ──
            dispositivos = []
            try:
                # Importar el módulo de descubrimiento nativo
                script_dir = os.path.dirname(os.path.abspath(__file__))
                if script_dir not in sys.path:
                    sys.path.insert(0, script_dir)
                from sadp_discover import discover as sadp_discover_native
                
                print("[DEBUG ScanThread] Usando descubrimiento SADP nativo (Python)")
                dispositivos = sadp_discover_native(timeout=12, debug=False)
                
                if dispositivos:
                    print(f"[DEBUG ScanThread] Descubrimiento nativo encontró {len(dispositivos)} dispositivo(s)")
                    self.devices.emit(dispositivos)
                    self.finished.emit()
                    return
                else:
                    print("[DEBUG ScanThread] Descubrimiento nativo: 0 dispositivos, intentando binario Go...")
            except ImportError:
                print("[DEBUG ScanThread] Módulo sadp_discover.py no disponible, usando binario Go")
            except Exception as native_err:
                print(f"[DEBUG ScanThread] Error en descubrimiento nativo: {native_err}, fallback a binario Go")

            # ── FALLBACK: Binario Go (sadp-linux-amd64) ──
            binario_path = obtener_binario_path()
            if not binario_path:
                if not dispositivos:
                    self.error.emit("No se encontró el binario SADP ni el módulo de descubrimiento nativo.\n\nAsegúrate de que 'sadp_discover.py' o 'sadp-linux-amd64' estén en el mismo directorio que gui_sadp.py o instalado en ~/.local/bin/sadp/")
                self.finished.emit()
                return
            
            # 1. Intentar primero obtener la salida en formato CSV (contiene campos de subred, gateway, DHCP)
            resultado_csv = subprocess.run(
                [binario_path, "discover:sadp", "--csv"],
                capture_output=True,
                text=True,
                timeout=30,
                check=False
            )
            
            if resultado_csv.returncode == 0 and "IPv4Address" in resultado_csv.stdout:
                try:
                    reader = csv.DictReader(io.StringIO(resultado_csv.stdout))
                    for row in reader:
                        ip = row.get('IPv4Address', '').strip()
                        mac = row.get('MAC', '').strip()
                        if not ip or not mac:
                            continue
                        
                        act_raw = row.get('Activated', '').strip().lower()
                        estado = "Active" if act_raw in ['true', 'active', 'activado'] else ("Inactive" if act_raw in ['false', 'inactive'] else row.get('Activated', 'Active'))
                        
                        dispositivos.append({
                            'ip': ip,
                            'mac': mac,
                            'tipo': row.get('DeviceType', '').strip(),
                            'estado': estado,
                            'puerto': row.get('Port', '8000').strip(),
                            'http_port': row.get('HttpPort', '80').strip(),
                            'serial': row.get('SerialNumber', '').strip(),
                            'version': row.get('SoftwareVersion', '').strip(),
                            'subnet': row.get('IPv4SubnetMask', '255.255.255.0').strip(),
                            'gateway': row.get('IPv4Gateway', '').strip(),
                            'dhcp': row.get('DHCP', 'false').strip()
                        })
                except Exception as csv_err:
                    print(f"[DEBUG ScanThread] Error parseando CSV SADP: {csv_err}")

            # 2. Fallback a la salida de tabla de texto plano si no se obtuvieron datos por CSV
            if not dispositivos:
                resultado = subprocess.run(
                    [binario_path, "discover:sadp"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=False
                )
                
                if resultado.returncode != 0 and not dispositivos:
                    error_msg = resultado.stderr.strip() if resultado.stderr else "Código de salida no cero sin mensaje de error."
                    self.error.emit(f"Error al ejecutar sadp (Código {resultado.returncode}):\n{error_msg}")
                    self.finished.emit()
                    return
                
                lineas = resultado.stdout.splitlines()
                for linea in lineas:
                    linea_clean = linea.strip()
                    if not linea_clean or linea_clean.startswith('#') or 'descubierto' in linea_clean.lower():
                        continue
                    
                    partes = linea_clean.split()
                    if len(partes) < 6:
                        continue
                    
                    idx_ip = -1
                    for i in range(min(3, len(partes))):
                        subpartes = partes[i].split('.')
                        if len(subpartes) == 4 and all(s.isdigit() for s in subpartes):
                            idx_ip = i
                            break
                    
                    if idx_ip == -1:
                        continue
                    
                    start_data = idx_ip
                    if len(partes) - start_data >= 6:
                        try:
                            ip      = partes[start_data]
                            mac     = partes[start_data + 1]
                            tipo    = partes[start_data + 2]
                            estado  = partes[start_data + 3]
                            puerto  = partes[start_data + 4]
                            serial  = partes[start_data + 5]
                            version = " ".join(partes[start_data + 6:]) if len(partes) > start_data + 6 else 'N/A'
                            
                            # Inferir gateway si no viene en texto
                            ip_parts = ip.split('.')
                            gw_inferred = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.1" if len(ip_parts) == 4 else ""

                            dispositivos.append({
                                'ip': ip,
                                'mac': mac,
                                'tipo': tipo,
                                'estado': estado,
                                'puerto': puerto,
                                'http_port': '80',
                                'serial': serial,
                                'version': version,
                                'subnet': '255.255.255.0',
                                'gateway': gw_inferred,
                                'dhcp': 'false'
                            })
                        except Exception as parse_err:
                            print(f"[DEBUG Parser] Error procesando línea: {linea_clean}. Detalle: {parse_err}")
                            pass
            
            self.devices.emit(dispositivos)
            self.finished.emit()
            
        except subprocess.TimeoutExpired:
            self.error.emit("Timeout: el escaneo tardó demasiado tiempo (límite de 30 segundos)")
            self.finished.emit()
        except Exception as e:
            self.error.emit(f"Error inesperado en el subproceso: {str(e)}")
            self.finished.emit()


class SADPGui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 1120, 650)
        self.scan_thread = None
        self.settings = QSettings("sadp", "sadp-gui-v2")
        
        # Cargar idioma preferido (inglés por defecto desde la raíz)
        self.current_lang = str(self.settings.value("appLanguage", "en"))
        if self.current_lang not in ("en", "es"):
            self.current_lang = "en"
        
        # --- Aplicar QSS Estilos Premium ---
        self.setStyleSheet("""
            QMainWindow {
                background-color: #FFFFFF;
            }
            QLabel {
                font-family: 'Segoe UI', 'Inter', 'Ubuntu', 'Arial', sans-serif;
                font-size: 12px;
                color: #374151;
            }
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #D1D5DB;
                border-radius: 4px;
                padding: 6px;
                color: #111827;
                font-family: 'Segoe UI', 'Inter', 'Ubuntu', sans-serif;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #0F83E6;
            }
            QLineEdit:disabled {
                background-color: #F3F4F6;
                color: #9CA3AF;
                border: 1px solid #E5E7EB;
            }
            QCheckBox {
                font-family: 'Segoe UI', 'Inter', 'Ubuntu', sans-serif;
                font-size: 12px;
                color: #374151;
                spacing: 5px;
            }
            QComboBox {
                background-color: #FFFFFF;
                border: 1px solid #D1D5DB;
                border-radius: 4px;
                padding: 4px 10px;
                color: #374151;
                font-family: 'Segoe UI', 'Inter', 'Ubuntu', sans-serif;
                font-size: 12px;
            }
            QComboBox:hover {
                border-color: #9CA3AF;
            }
            QComboBox::drop-down {
                border: none;
                width: 18px;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                border: 1px solid #D1D5DB;
                selection-background-color: #E0F2FE;
                selection-color: #0369A1;
            }
            QPushButton.btn-coral {
                background-color: #E58B8B;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                font-family: 'Segoe UI', 'Inter', 'Ubuntu', sans-serif;
                font-size: 12px;
            }
            QPushButton.btn-coral:hover {
                background-color: #DB7A7A;
            }
            QPushButton.btn-coral:pressed {
                background-color: #C66B6B;
            }
            QPushButton.btn-coral:disabled {
                background-color: #F3D8D8;
                color: #F9C0C0;
            }
            QPushButton.btn-outline {
                background-color: #FFFFFF;
                color: #374151;
                border: 1px solid #D1D5DB;
                border-radius: 4px;
                padding: 8px 16px;
                font-family: 'Segoe UI', 'Inter', 'Ubuntu', sans-serif;
                font-size: 12px;
            }
            QPushButton.btn-outline:hover {
                background-color: #F9FAFB;
                border-color: #9CA3AF;
            }
            QPushButton.btn-outline:pressed {
                background-color: #F3F4F6;
            }
            QPushButton.btn-outline:disabled {
                background-color: #FFFFFF;
                color: #D1D5DB;
                border-color: #E5E7EB;
            }
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                gridline-color: #F3F4F6;
                font-family: 'Segoe UI', 'Inter', 'Ubuntu', sans-serif;
                font-size: 12px;
                color: #111827;
            }
            QHeaderView::section {
                background-color: #47505A;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 11px;
                padding: 6px;
                border: 1px solid #3C444D;
            }
            QTableWidget::item:selected {
                background-color: #E0F2FE;
                color: #0369A1;
            }
            QProgressBar {
                border: 1px solid #E5E7EB;
                border-radius: 4px;
                text-align: center;
                background-color: #F3F4F6;
            }
            QProgressBar::chunk {
                background-color: #0F83E6;
                border-radius: 3px;
            }
        """)

        # Main Layout Horizontal (Lado Izquierdo = Tabla, Lado Derecho = Parámetros de Red)
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_h_layout = QHBoxLayout(self.main_widget)
        self.main_h_layout.setContentsMargins(15, 15, 15, 15)
        self.main_h_layout.setSpacing(15)

        # ==========================================
        # --- COLUMNA IZQUIERDA (Dashboard + Tabla) ---
        # ==========================================
        self.left_widget = QWidget()
        self.left_layout = QVBoxLayout(self.left_widget)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(10)

        # 1. Barra de herramientas superior (Estilo SADP original)
        self.top_layout = QHBoxLayout()
        
        # Etiqueta de conteo
        self.lbl_count = QLabel()
        self.top_layout.addWidget(self.lbl_count)
        
        self.top_layout.addStretch()

        # Selector de Idioma (Language switcher)
        self.combo_lang = QComboBox()
        self.combo_lang.addItem("🌐 English", "en")
        self.combo_lang.addItem("🌐 Español", "es")
        self.combo_lang.setMinimumHeight(35)
        self.combo_lang.setCurrentIndex(0 if self.current_lang == "en" else 1)
        self.combo_lang.currentIndexChanged.connect(self.cambiar_idioma)
        self.top_layout.addWidget(self.combo_lang)

        # Botón Unbind
        self.btn_unbind = QPushButton()
        self.btn_unbind.setProperty("class", "btn-coral")
        self.btn_unbind.setMinimumHeight(35)
        self.btn_unbind.setEnabled(False)
        self.btn_unbind.clicked.connect(self.desvincular_dispositivo)
        self.top_layout.addWidget(self.btn_unbind)

        # Botón Export
        self.btn_export = QPushButton()
        self.btn_export.setProperty("class", "btn-coral")
        self.btn_export.setMinimumHeight(35)
        self.btn_export.setEnabled(False)
        self.btn_export.clicked.connect(self.exportar_csv)
        self.top_layout.addWidget(self.btn_export)

        # Botón Refresh
        self.btn_scan = QPushButton()
        self.btn_scan.setProperty("class", "btn-outline")
        self.btn_scan.setMinimumHeight(35)
        self.btn_scan.clicked.connect(self.ejecutar_escaneo)
        self.top_layout.addWidget(self.btn_scan)

        # Entrada de Filtrado (Filter)
        self.txt_filter = QLineEdit()
        self.txt_filter.setMaximumWidth(160)
        self.txt_filter.setMinimumHeight(30)
        self.txt_filter.textChanged.connect(self.filtrar_tabla)
        self.top_layout.addWidget(self.txt_filter)

        # Botón Toggle Panel (Modificar Red)
        self.btn_toggle_panel = QPushButton()
        self.btn_toggle_panel.setProperty("class", "btn-outline")
        self.btn_toggle_panel.setMinimumHeight(35)
        self.btn_toggle_panel.clicked.connect(self.toggle_panel)
        self.top_layout.addWidget(self.btn_toggle_panel)

        self.left_layout.addLayout(self.top_layout)

        # 2. Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(0)  # Modo indeterminado
        self.progress_bar.setVisible(False)
        self.left_layout.addWidget(self.progress_bar)

        # 3. Etiqueta de estado
        self.status_label = QLabel()
        self.left_layout.addWidget(self.status_label)

        # 4. Tabla de dispositivos (8 columnas)
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(8)
        
        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.tabla.setColumnWidth(0, 35)
        header.setSectionsClickable(True)
        header.setSortIndicatorShown(True)
        
        self.tabla.setSelectionBehavior(self.tabla.SelectionBehavior.SelectRows)
        self.tabla.cellClicked.connect(self.seleccionar_fila)
        self.tabla.cellDoubleClicked.connect(self.doble_clic_celda)
        self.tabla.cellChanged.connect(self.modelo_celda_cambiada)
        
        # Restaurar estado del encabezado si existe
        try:
            state = self.settings.value("headerStateV4")
            if state is not None:
                header.restoreState(state)
        except Exception:
            pass

        # Restaurar columna/orden de ordenación
        try:
            sort_col = self.settings.value("sortColumnV4")
            sort_order = self.settings.value("sortOrderV4")
            if sort_col is not None:
                sort_col = int(sort_col)
                sort_order = int(sort_order) if sort_order is not None else int(Qt.SortOrder.AscendingOrder)
                self.tabla.sortItems(sort_col, Qt.SortOrder(sort_order))
        except Exception:
            pass

        header.sectionMoved.connect(self.save_header_state)
        header.sectionResized.connect(self.save_header_state)
        header.sortIndicatorChanged.connect(self.save_sort_indicator)
        self.tabla.setSortingEnabled(True)
        self.left_layout.addWidget(self.tabla)

        # ==========================================
        # --- COLUMNA DERECHA (Panel Modificar - Desplegable) ---
        # ==========================================
        self.panel_modificar = QFrame()
        self.panel_modificar.setFrameShape(QFrame.Shape.StyledPanel)
        self.panel_modificar.setObjectName("PanelModificar")
        self.panel_modificar.setStyleSheet("""
            #PanelModificar {
                background-color: #F9FAFB;
                border-left: 1px solid #E5E7EB;
                border-radius: 4px;
            }
        """)
        
        self.right_layout = QVBoxLayout(self.panel_modificar)
        self.right_layout.setContentsMargins(10, 10, 10, 10)
        self.right_layout.setSpacing(10)

        # Cabecera del Panel (Título + Botón Cerrar)
        panel_header = QHBoxLayout()
        self.lbl_panel_title = QLabel()
        self.lbl_panel_title.setStyleSheet("font-weight: bold; font-size: 13px; color: #111827;")
        panel_header.addWidget(self.lbl_panel_title)
        
        panel_header.addStretch()
        
        btn_close_panel = QPushButton("✕")
        btn_close_panel.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 14px;
                color: #9CA3AF;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #EF4444;
            }
        """)
        btn_close_panel.clicked.connect(self.panel_modificar.hide)
        btn_close_panel.clicked.connect(lambda: self.btn_toggle_panel.setText(self.t("modify_network")))
        panel_header.addWidget(btn_close_panel)
        
        self.right_layout.addLayout(panel_header)

        # Scroll Area para que todos los campos entren cómodamente
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("background-color: transparent;")
        
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background-color: transparent;")
        self.scroll_layout = QVBoxLayout(scroll_widget)
        self.scroll_layout.setContentsMargins(0, 5, 0, 5)
        self.scroll_layout.setSpacing(10)

        # Checkboxes (DHCP / Hik-Connect)
        self.chk_dhcp = QCheckBox()
        self.chk_dhcp.setEnabled(False)
        self.chk_dhcp.stateChanged.connect(self.toggle_dhcp_fields)
        self.scroll_layout.addWidget(self.chk_dhcp)
        
        self.chk_hik = QCheckBox()
        self.chk_hik.setEnabled(False)
        self.scroll_layout.addWidget(self.chk_hik)

        # Campos de texto individuales
        self.lbl_model = QLabel()
        self.scroll_layout.addWidget(self.lbl_model)
        self.txt_model = QLineEdit()
        self.txt_model.setEnabled(False)
        self.txt_model.textChanged.connect(self.guardar_modelo_panel)
        self.scroll_layout.addWidget(self.txt_model)

        self.lbl_serial = QLabel()
        self.scroll_layout.addWidget(self.lbl_serial)
        self.txt_serial = QLineEdit()
        self.txt_serial.setReadOnly(True)
        self.scroll_layout.addWidget(self.txt_serial)

        self.lbl_ip = QLabel()
        self.scroll_layout.addWidget(self.lbl_ip)
        self.txt_ip = QLineEdit()
        self.txt_ip.setEnabled(False)
        self.scroll_layout.addWidget(self.txt_ip)

        self.lbl_port = QLabel()
        self.scroll_layout.addWidget(self.lbl_port)
        self.txt_port = QLineEdit()
        self.txt_port.setEnabled(False)
        self.scroll_layout.addWidget(self.txt_port)

        self.lbl_sdk_port = QLabel()
        self.scroll_layout.addWidget(self.lbl_sdk_port)
        self.txt_sdk_port = QLineEdit()
        self.txt_sdk_port.setEnabled(False)
        self.scroll_layout.addWidget(self.txt_sdk_port)

        self.lbl_subnet = QLabel()
        self.scroll_layout.addWidget(self.lbl_subnet)
        self.txt_subnet = QLineEdit()
        self.txt_subnet.setEnabled(False)
        self.scroll_layout.addWidget(self.txt_subnet)

        self.lbl_gateway = QLabel()
        self.scroll_layout.addWidget(self.lbl_gateway)
        self.txt_gateway = QLineEdit()
        self.txt_gateway.setEnabled(False)
        self.scroll_layout.addWidget(self.txt_gateway)

        self.lbl_ipv6 = QLabel()
        self.scroll_layout.addWidget(self.lbl_ipv6)
        self.txt_ipv6 = QLineEdit()
        self.txt_ipv6.setEnabled(False)
        self.scroll_layout.addWidget(self.txt_ipv6)

        self.lbl_ipv6_gw = QLabel()
        self.scroll_layout.addWidget(self.lbl_ipv6_gw)
        self.txt_ipv6_gw = QLineEdit()
        self.txt_ipv6_gw.setEnabled(False)
        self.scroll_layout.addWidget(self.txt_ipv6_gw)

        self.lbl_ipv6_prefix = QLabel()
        self.scroll_layout.addWidget(self.lbl_ipv6_prefix)
        self.txt_ipv6_prefix = QLineEdit()
        self.txt_ipv6_prefix.setEnabled(False)
        self.scroll_layout.addWidget(self.txt_ipv6_prefix)

        self.lbl_http_port = QLabel()
        self.scroll_layout.addWidget(self.lbl_http_port)
        self.txt_http_port = QLineEdit()
        self.txt_http_port.setEnabled(False)
        self.scroll_layout.addWidget(self.txt_http_port)

        # Línea divisoria para verificación de seguridad
        linea = QFrame()
        linea.setFrameShape(QFrame.Shape.HLine)
        linea.setFrameShadow(QFrame.Shadow.Sunken)
        linea.setStyleSheet("color: #E5E7EB;")
        self.scroll_layout.addWidget(linea)

        # Sección de Seguridad
        self.lbl_sec = QLabel()
        self.lbl_sec.setStyleSheet("font-weight: bold; color: #4B5563; margin-top: 5px;")
        self.scroll_layout.addWidget(self.lbl_sec)

        self.lbl_password = QLabel()
        self.scroll_layout.addWidget(self.lbl_password)
        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_password.setEnabled(False)
        self.scroll_layout.addWidget(self.txt_password)

        # Botón Modificar
        self.btn_modify = QPushButton()
        self.btn_modify.setProperty("class", "btn-coral")
        self.btn_modify.setMinimumHeight(35)
        self.btn_modify.setEnabled(False)
        self.btn_modify.clicked.connect(self.ejecutar_modificacion)
        self.scroll_layout.addWidget(self.btn_modify)

        # Forgot Password Link
        self.lbl_forgot = QLabel()
        self.lbl_forgot.setOpenExternalLinks(False)
        self.lbl_forgot.linkActivated.connect(self.recuperar_contrasena)
        self.lbl_forgot.setStyleSheet("margin-top: 5px;")
        self.scroll_layout.addWidget(self.lbl_forgot)

        scroll_area.setWidget(scroll_widget)
        self.right_layout.addWidget(scroll_area)

        # Agregar ambas columnas al layout horizontal
        self.main_h_layout.addWidget(self.left_widget, stretch=7)
        self.main_h_layout.addWidget(self.panel_modificar, stretch=3)

        # Ocultar panel lateral por defecto (requerido por el usuario)
        self.panel_modificar.hide()

        # Dispositivos en caché
        self.dispositivos = []

        # Inicializar todos los textos en el idioma configurado (inglés por defecto)
        self.retranslate_ui()

    def t(self, key: str, **kwargs) -> str:
        """Helper para obtener texto traducido en el idioma activo"""
        return t(key, lang=self.current_lang, **kwargs)

    def cambiar_idioma(self, index: int):
        """Cambia el idioma de la aplicación y refresca la UI inmediatamente"""
        new_lang = self.combo_lang.currentData()
        if new_lang and new_lang != self.current_lang:
            self.current_lang = new_lang
            self.settings.setValue("appLanguage", new_lang)
            self.retranslate_ui()

    def retranslate_ui(self):
        """Aplica las traducciones dinámicamente a todos los componentes de la interfaz"""
        self.setWindowTitle(self.t("app_title"))
        self.lbl_count.setText(f"{self.t('total_devices')} <b style='color:#0F83E6; font-size:16px;'>{len(self.dispositivos)}</b>")
        self.btn_unbind.setText(self.t("unbind"))
        self.btn_export.setText(self.t("export"))
        self.btn_scan.setText(self.t("refresh"))
        self.txt_filter.setPlaceholderText(self.t("filter"))

        if self.panel_modificar.isVisible():
            self.btn_toggle_panel.setText(self.t("hide_panel"))
        else:
            self.btn_toggle_panel.setText(self.t("modify_network"))

        if not self.scan_thread or not self.scan_thread.isRunning():
            if self.dispositivos:
                self.status_label.setText(self.t("found_devices", count=len(self.dispositivos)))
            else:
                self.status_label.setText(self.t("press_refresh"))

        # Encabezados de tabla
        headers = [
            self.t("col_select"),
            self.t("col_ip"),
            self.t("col_mac"),
            self.t("col_model"),
            self.t("col_type"),
            self.t("col_status"),
            self.t("col_port"),
            self.t("col_version")
        ]
        self.tabla.setHorizontalHeaderLabels(headers)

        # Actualizar columna de tipo en las filas cargadas
        self.tabla.blockSignals(True)
        for r in range(self.tabla.rowCount()):
            mac_item = self.tabla.item(r, 2)
            if mac_item:
                mac = mac_item.text().strip()
                for d in self.dispositivos:
                    if d.get('mac') == mac:
                        type_str = translate_device_type(d.get('tipo', ''), d.get('serial', ''), lang=self.current_lang)
                        self.tabla.setItem(r, 4, SortableItem(type_str, sort_key=type_str))
                        break
        self.tabla.blockSignals(False)

        # Panel lateral
        self.lbl_panel_title.setText(self.t("panel_title"))
        self.chk_dhcp.setText(self.t("enable_dhcp"))
        self.chk_hik.setText(self.t("enable_hik"))
        self.lbl_model.setText(self.t("field_model"))
        self.txt_model.setPlaceholderText(self.t("placeholder_model"))
        self.txt_model.setToolTip(self.t("tooltip_model"))
        self.lbl_serial.setText(self.t("field_serial"))
        self.txt_serial.setToolTip(self.t("tooltip_serial"))
        self.lbl_ip.setText(self.t("field_ip"))
        self.lbl_port.setText(self.t("field_port"))
        self.lbl_sdk_port.setText(self.t("field_sdk_port"))
        self.lbl_subnet.setText(self.t("field_subnet"))
        self.lbl_gateway.setText(self.t("field_gateway"))
        self.lbl_ipv6.setText(self.t("field_ipv6"))
        self.lbl_ipv6_gw.setText(self.t("field_ipv6_gw"))
        self.lbl_ipv6_prefix.setText(self.t("field_ipv6_prefix"))
        self.lbl_http_port.setText(self.t("field_http_port"))
        self.lbl_sec.setText(self.t("sec_verification"))
        self.lbl_password.setText(self.t("admin_password"))
        self.txt_password.setPlaceholderText(self.t("enter_password"))
        self.btn_modify.setText(self.t("modify"))
        self.lbl_forgot.setText(f'<a href="#forgot" style="color: #0F83E6; text-decoration: none; font-weight: 500;">{self.t("forgot_password")}</a>')

    def toggle_panel(self):
        """Muestra u oculta el panel lateral de modificación de red"""
        if self.panel_modificar.isVisible():
            self.panel_modificar.hide()
            self.btn_toggle_panel.setText(self.t("modify_network"))
        else:
            self.panel_modificar.show()
            self.btn_toggle_panel.setText(self.t("hide_panel"))

    def toggle_dhcp_fields(self, state):
        """Habilita o deshabilita los campos de IP si DHCP está activo"""
        is_dhcp = (state == Qt.CheckState.Checked.value)
        # Si DHCP está activado, los campos de IP se autodefinen por la red, por ende se desactivan
        self.txt_ip.setDisabled(is_dhcp)
        self.txt_subnet.setDisabled(is_dhcp)
        self.txt_gateway.setDisabled(is_dhcp)

    def ejecutar_escaneo(self):
        """Inicia el escaneo en un thread aparte"""
        if self.scan_thread and self.scan_thread.isRunning():
            QMessageBox.warning(self, self.t("scan_in_progress_title"), self.t("scan_in_progress_msg"))
            return
        
        self.tabla.setRowCount(0)
        self.dispositivos = []
        self.btn_scan.setEnabled(False)
        self.btn_export.setEnabled(False)
        self.btn_unbind.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_label.setText(self.t("scanning"))
        self.lbl_count.setText(f"{self.t('total_devices')} <b style='color:#0F83E6; font-size:16px;'>0</b>")
        
        # Limpiar formulario
        self.txt_model.clear()
        self.txt_serial.clear()
        self.txt_ip.clear()
        self.txt_port.clear()
        self.txt_sdk_port.clear()
        self.txt_subnet.clear()
        self.txt_gateway.clear()
        self.txt_ipv6.clear()
        self.txt_ipv6_gw.clear()
        self.txt_ipv6_prefix.clear()
        self.txt_http_port.clear()
        self.txt_password.clear()
        self.chk_dhcp.setChecked(False)
        self.chk_hik.setChecked(False)
        
        # Deshabilitar controles del panel
        self.txt_model.setEnabled(False)
        self.txt_ip.setEnabled(False)
        self.txt_port.setEnabled(False)
        self.txt_sdk_port.setEnabled(False)
        self.txt_subnet.setEnabled(False)
        self.txt_gateway.setEnabled(False)
        self.txt_http_port.setEnabled(False)
        self.txt_ipv6.setEnabled(False)
        self.txt_ipv6_gw.setEnabled(False)
        self.txt_ipv6_prefix.setEnabled(False)
        self.chk_dhcp.setEnabled(False)
        self.chk_hik.setEnabled(False)
        self.txt_password.setEnabled(False)
        self.btn_modify.setEnabled(False)
        
        self.scan_thread = ScanThread()
        self.scan_thread.devices.connect(self.mostrar_dispositivos)
        self.scan_thread.error.connect(self.mostrar_error)
        self.scan_thread.finished.connect(self.escaneo_finalizado)
        self.scan_thread.start()

    def mostrar_dispositivos(self, dispositivos):
        """Muestra los dispositivos en la tabla"""
        self.dispositivos = dispositivos
        self.lbl_count.setText(f"{self.t('total_devices')} <b style='color:#0F83E6; font-size:16px;'>{len(dispositivos)}</b>")
        
        if not dispositivos:
            self.status_label.setText(self.t("no_devices"))
            return
        
        # Desactivar señales y ordenación mientras se insertan filas
        self.tabla.blockSignals(True)
        self.tabla.setSortingEnabled(False)
        for idx, disp in enumerate(dispositivos):
            row_position = self.tabla.rowCount()
            self.tabla.insertRow(row_position)
            
            # Checkbox en la columna 0 (SADP original style)
            chk_item = QTableWidgetItem()
            chk_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            chk_item.setCheckState(Qt.CheckState.Unchecked)
            self.tabla.setItem(row_position, 0, chk_item)

            # IP (columna 1)
            ip_text = disp.get('ip', '')
            try:
                ip_key = tuple(int(x) for x in ip_text.split('.') if x != '')
            except Exception:
                ip_key = ip_text
            self.tabla.setItem(row_position, 1, SortableItem(ip_text, sort_key=ip_key))

            # MAC (columna 2)
            mac_text = disp.get('mac', '')
            mac_key = mac_text.replace(':', '').replace('-', '').lower()
            self.tabla.setItem(row_position, 2, SortableItem(mac_text, sort_key=mac_key))

            # Modelo (columna 3) - Nombre de modelo del equipo (ej. DS-9664NI-I8)
            default_modelo = disp.get('nombre') or disp.get('tipo') or ''
            modelo_guardado = self.settings.value(f"modelo/{mac_text.upper()}", default_modelo)
            disp['modelo'] = str(modelo_guardado) if modelo_guardado is not None else default_modelo
            modelo_item = SortableItem(disp['modelo'], sort_key=disp['modelo'])
            modelo_item.setFlags(modelo_item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.tabla.setItem(row_position, 3, modelo_item)

            # Tipo de Dispositivo (columna 4)
            tipo_raw = disp.get('tipo', '')
            serial_raw = disp.get('serial', '')
            tipo_text = translate_device_type(tipo_raw, serial_raw, lang=self.current_lang)
            self.tabla.setItem(row_position, 4, SortableItem(tipo_text, sort_key=tipo_text))

            # Estado (columna 5)
            estado_text = disp.get('estado', '')
            self.tabla.setItem(row_position, 5, SortableItem(estado_text, sort_key=estado_text))

            # Puerto (columna 6)
            puerto_text = disp.get('puerto', '')
            try:
                puerto_key = int(puerto_text)
            except Exception:
                puerto_key = puerto_text
            self.tabla.setItem(row_position, 6, SortableItem(puerto_text, sort_key=puerto_key))

            # Version (columna 7)
            version_text = disp.get('version', '')
            self.tabla.setItem(row_position, 7, SortableItem(version_text, sort_key=version_text))
        
        # Volver a activar señales y ordenación después de insertar todas las filas
        self.tabla.blockSignals(False)
        self.tabla.setSortingEnabled(True)
        self.status_label.setText(self.t("found_devices", count=len(dispositivos)))

    def save_header_state(self, *args):
        try:
            header = self.tabla.horizontalHeader()
            state = header.saveState()
            self.settings.setValue("headerStateV4", state)
        except Exception:
            pass

    def save_sort_indicator(self, index: int, order: Qt.SortOrder):
        try:
            self.settings.setValue("sortColumnV4", int(index))
            self.settings.setValue("sortOrderV4", int(order))
        except Exception:
            pass

    def closeEvent(self, event):
        # Guardar estado al cerrar
        try:
            self.save_header_state()
        except Exception:
            pass
        super().closeEvent(event)

    def modelo_celda_cambiada(self, row, column):
        """Guardar modelo cuando se edita directamente la celda de la columna Modelo (col 3)"""
        if column != 3:
            return
        mac_item = self.tabla.item(row, 2)
        modelo_item = self.tabla.item(row, 3)
        if mac_item and modelo_item:
            mac = mac_item.text().strip()
            nuevo_modelo = modelo_item.text().strip()
            if mac:
                self.settings.setValue(f"modelo/{mac.upper()}", nuevo_modelo)
                if getattr(self, 'selected_device_mac', '').upper() == mac.upper():
                    self.txt_model.blockSignals(True)
                    self.txt_model.setText(nuevo_modelo)
                    self.txt_model.blockSignals(False)

    def guardar_modelo_panel(self, nuevo_modelo):
        """Guardar modelo cuando se edita el campo 'Modelo' en el panel lateral"""
        mac = getattr(self, 'selected_device_mac', '').strip()
        if not mac:
            return
        
        self.settings.setValue(f"modelo/{mac.upper()}", nuevo_modelo.strip())
        
        # Actualizar celda en la tabla
        self.tabla.blockSignals(True)
        for r in range(self.tabla.rowCount()):
            mac_item = self.tabla.item(r, 2)
            if mac_item and mac_item.text().strip().upper() == mac.upper():
                modelo_item = self.tabla.item(r, 3)
                if modelo_item:
                    modelo_item.setText(nuevo_modelo)
                break
        self.tabla.blockSignals(False)

    def mostrar_error(self, mensaje):
        """Muestra un error"""
        QMessageBox.critical(self, self.t("scan_error"), f"{mensaje}")
        self.status_label.setText(self.t("scan_error"))

    def escaneo_finalizado(self):
        """Llamado cuando el escaneo termina"""
        self.btn_scan.setEnabled(True)
        if self.dispositivos:
            self.btn_export.setEnabled(True)
            self.btn_unbind.setEnabled(True)
        self.progress_bar.setVisible(False)

    def seleccionar_fila(self, row, column):
        """Selecciona una fila, marca su checkbox y rellena el panel lateral con datos de red reales"""
        self.tabla.blockSignals(True)
        try:
            for r in range(self.tabla.rowCount()):
                item = self.tabla.item(r, 0)
                if item:
                    item.setCheckState(Qt.CheckState.Unchecked)
            curr_item = self.tabla.item(row, 0)
            if curr_item:
                curr_item.setCheckState(Qt.CheckState.Checked)
        finally:
            self.tabla.blockSignals(False)

        # Cargar datos desde la fila seleccionada
        ip = self.tabla.item(row, 1).text() if self.tabla.item(row, 1) else ""
        mac = self.tabla.item(row, 2).text() if self.tabla.item(row, 2) else ""
        modelo = self.tabla.item(row, 3).text() if self.tabla.item(row, 3) else ""
        puerto = self.tabla.item(row, 6).text() if self.tabla.item(row, 6) else "8000"

        # Guardar MAC e IP seleccionadas autoritativas
        self.selected_device_mac = mac
        self.selected_device_ip = ip

        # Buscar registro detallado en la caché de dispositivos
        disp_data = None
        for disp in self.dispositivos:
            if mac and disp.get('mac') == mac:
                disp_data = disp
                break

        serial = disp_data.get('serial', '') if disp_data else ""

        # Poblar formulario lateral
        self.txt_model.blockSignals(True)
        self.txt_model.setText(modelo)
        self.txt_model.blockSignals(False)
        self.txt_serial.setText(serial)
        self.txt_ip.setText(ip)
        
        if disp_data:
            self.txt_port.setText(disp_data.get('puerto', puerto))
            self.txt_sdk_port.setText(disp_data.get('puerto', puerto if puerto else "8000"))
            self.txt_subnet.setText(disp_data.get('subnet', "255.255.255.0"))
            self.txt_gateway.setText(disp_data.get('gateway', ""))
            self.txt_http_port.setText(disp_data.get('http_port', "80"))
            self.chk_dhcp.setChecked(disp_data.get('dhcp', '').lower() == 'true')
        else:
            self.txt_port.setText(puerto)
            self.txt_sdk_port.setText("8000")
            self.txt_subnet.setText("255.255.255.0")
            parts = ip.split('.')
            if len(parts) == 4:
                self.txt_gateway.setText(f"{parts[0]}.{parts[1]}.{parts[2]}.1")
            else:
                self.txt_gateway.setText("")
            self.txt_http_port.setText("80")
            self.chk_dhcp.setChecked(False)

        self.txt_ipv6.setText("")
        self.txt_ipv6_gw.setText("")
        self.txt_ipv6_prefix.setText("64")
        self.txt_password.clear()
        
        # Habilitar controles del formulario
        self.txt_model.setEnabled(True)
        
        # Habilitar controles del formulario
        self.txt_ip.setEnabled(True)
        self.txt_port.setEnabled(True)
        self.txt_sdk_port.setEnabled(True)
        self.txt_subnet.setEnabled(True)
        self.txt_gateway.setEnabled(True)
        self.txt_http_port.setEnabled(True)
        self.txt_ipv6.setEnabled(True)
        self.txt_ipv6_gw.setEnabled(True)
        self.txt_ipv6_prefix.setEnabled(True)
        self.chk_dhcp.setEnabled(True)
        self.chk_hik.setEnabled(True)
        self.txt_password.setEnabled(True)
        self.btn_modify.setEnabled(True)
        self.btn_unbind.setEnabled(True)

    def doble_clic_celda(self, row, column):
        """Maneja el doble clic en la IP (columna 1) para abrir en el navegador"""
        if column == 1:
            item_ip = self.tabla.item(row, column)
            if item_ip:
                ip = item_ip.text()
                url = f"http://{ip}"
                
                respuesta = QMessageBox.question(
                    self,
                    self.t("open_browser_title"),
                    self.t("open_browser_msg", ip=ip),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if respuesta == QMessageBox.StandardButton.Yes:
                    webbrowser.open(url)
                    self.status_label.setText(self.t("opening_browser", url=url))

    def filtrar_tabla(self, texto):
        """Filtra en tiempo real los dispositivos mostrados según el texto de búsqueda"""
        texto = texto.lower().strip()
        for row in range(self.tabla.rowCount()):
            mostrar_fila = False
            if not texto:
                mostrar_fila = True
            else:
                for col in range(1, self.tabla.columnCount()):
                    item = self.tabla.item(row, col)
                    if item and texto in item.text().lower():
                        mostrar_fila = True
                        break
            self.tabla.setRowHidden(row, not mostrar_fila)

    def ejecutar_modificacion(self):
        """Ejecuta el cambio de parámetros de red vía tramas SADP UDP multicast/broadcast"""
        mac = getattr(self, 'selected_device_mac', '').strip()
        current_ip = getattr(self, 'selected_device_ip', '').strip()
        new_ip = self.txt_ip.text().strip()
        subnet = self.txt_subnet.text().strip()
        gateway = self.txt_gateway.text().strip()
        port = self.txt_sdk_port.text().strip() or self.txt_port.text().strip() or "8000"
        dhcp = self.chk_dhcp.isChecked()
        password = self.txt_password.text()

        if not mac:
            QMessageBox.warning(self, self.t("select_device_title"), self.t("select_device_msg"))
            return

        if not password:
            QMessageBox.warning(self, self.t("password_req_title"), self.t("password_req_msg"))
            return

        if not dhcp:
            if not new_ip or len(new_ip.split('.')) != 4:
                QMessageBox.warning(self, self.t("invalid_ip_title"), self.t("invalid_ip_msg"))
                return
            if not subnet or len(subnet.split('.')) != 4:
                QMessageBox.warning(self, self.t("invalid_subnet_title"), self.t("invalid_subnet_msg"))
                return

        binario_path = obtener_binario_path()
        if not binario_path:
            QMessageBox.critical(self, self.t("binary_not_found_title"), self.t("binary_not_found_msg"))
            return

        self.btn_modify.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_label.setText(self.t("sending_changes", mac=mac, new_ip=new_ip))

        self.modify_thread = ModifyThread(
            binario_path=binario_path,
            current_ip=current_ip,
            mac=mac,
            password=password,
            new_ip=new_ip,
            mask=subnet,
            gateway=gateway,
            port=port,
            dhcp=dhcp
        )
        self.modify_thread.finished.connect(self._modificacion_finalizada)
        self.modify_thread.start()

    def _modificacion_finalizada(self, exito: bool, mensaje: str):
        self.btn_modify.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.txt_password.clear()
        
        if exito:
            dhcp_status = self.t("enabled") if self.chk_dhcp.isChecked() else self.t("disabled")
            QMessageBox.information(
                self,
                self.t("modify_success_title"),
                self.t("modify_success_msg", 
                       ip=self.txt_ip.text(), 
                       subnet=self.txt_subnet.text(), 
                       gateway=self.txt_gateway.text(), 
                       dhcp=dhcp_status)
            )
            self.status_label.setText(self.t("modify_success_title"))
            self.ejecutar_escaneo()
        else:
            QMessageBox.critical(self, self.t("modify_error_title"), mensaje)
            self.status_label.setText(self.t("modify_error_title"))

    def desvincular_dispositivo(self):
        """Desvincula el dispositivo de la cuenta Hik-Connect/Ezviz usando la contraseña admin"""
        mac = getattr(self, 'selected_device_mac', '').strip()
        current_ip = getattr(self, 'selected_device_ip', '').strip()
        password = self.txt_password.text()

        if not mac:
            QMessageBox.warning(self, self.t("select_device_title"), self.t("select_device_msg"))
            return

        if not password:
            QMessageBox.warning(self, self.t("password_req_title"), self.t("password_unbind_req_msg"))
            return

        confirmacion = QMessageBox.question(
            self,
            self.t("confirm_unbind_title"),
            self.t("confirm_unbind_msg", mac=mac),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirmacion != QMessageBox.StandardButton.Yes:
            return

        binario_path = obtener_binario_path()
        if not binario_path:
            QMessageBox.critical(self, self.t("binary_not_found_title"), self.t("binary_not_found_msg"))
            return

        self.btn_unbind.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_label.setText(self.t("unbinding_device", mac=mac))

        self.unbind_thread = UnbindThread(
            binario_path=binario_path,
            current_ip=current_ip,
            mac=mac,
            password=password
        )
        self.unbind_thread.finished.connect(self._desvinculacion_finalizada)
        self.unbind_thread.start()

    def _desvinculacion_finalizada(self, exito: bool, mensaje: str):
        self.btn_unbind.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.txt_password.clear()
        
        if exito:
            QMessageBox.information(self, self.t("unbind_success_title"), mensaje)
            self.status_label.setText(self.t("unbind_success_title"))
        else:
            QMessageBox.critical(self, self.t("unbind_error_title"), mensaje)
            self.status_label.setText(self.t("unbind_error_title"))

    def recuperar_contrasena(self, link=None):
        """Explica el flujo local offline para recuperar contraseña"""
        QMessageBox.information(
            self,
            self.t("forgot_password_title"),
            self.t("forgot_password_msg")
        )

    def exportar_csv(self):
        """Exporta los dispositivos a un archivo CSV"""
        if not self.dispositivos:
            QMessageBox.warning(self, self.t("no_data_title"), self.t("no_data_msg"))
            return
        
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self,
                self.t("export_dialog_title"),
                "hikvision_devices.csv",
                self.t("csv_filter")
            )
            if not filename:
                return

            fieldnames = [
                'ip', 'mac', 'modelo', 'tipo', 'estado', 'puerto', 
                'http_port', 'version', 'subnet', 'gateway', 'dhcp'
            ]

            rows_to_write = []
            for disp in self.dispositivos:
                row = dict(disp)
                mac_raw = row.get('mac', '')
                default_mod = row.get('nombre') or row.get('tipo') or ''
                mod_val = self.settings.value(f"modelo/{mac_raw.upper()}", default_mod)
                row['modelo'] = str(mod_val) if mod_val is not None else default_mod
                # Traducir el tipo para que sea legible en el CSV
                tipo_raw = row.get('tipo', '')
                serial_raw = row.get('serial', '')
                row['tipo'] = translate_device_type(tipo_raw, serial_raw, lang=self.current_lang)
                rows_to_write.append(row)

            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(rows_to_write)
            
            QMessageBox.information(
                self, 
                self.t("export_success_title"), 
                self.t("export_success_msg", count=len(rows_to_write), filename=filename)
            )
            self.status_label.setText(self.t("exported", filename=os.path.basename(filename)))
        except Exception as e:
            QMessageBox.critical(self, self.t("export_error_title"), self.t("export_error_msg", error=str(e)))



if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = SADPGui()
    ventana.show()
    sys.exit(app.exec())