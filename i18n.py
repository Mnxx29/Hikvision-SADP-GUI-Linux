"""
i18n.py - Internationalization and Localization for Hikvision SADP GUI.
English is the default language, with full Spanish support and dynamic switching.
"""

TRANSLATIONS = {
    "en": {
        # App & Window
        "app_title": "SADP for Linux",
        "brand_subtitle": "Hikvision device discovery · by mnxx29",
        "settings": "Settings",
        "language": "Language",
        "total_devices": "Online devices:",
        "unbind": "Unbind",
        "export": "Export",
        "refresh": "Scan network",
        "filter": "Filter",
        "modify_network": "Network settings",
        "hide_panel": "Hide settings",
        
        # Status Messages
        "press_refresh": "Scan the network to discover devices",
        "scanning": "Scanning devices... please wait",
        "found_devices": "✅ Found {count} device(s)",
        "no_devices": "⚠️ No Hikvision devices found on the network",
        "scan_error": "❌ Error during scan",
        "opening_browser": "Opening {url} in browser...",
        "sending_changes": "Sending network changes to {mac} ({new_ip})... please wait",
        "unbinding_device": "Unbinding device {mac}...",
        "exported": "Exported: {filename}",

        # Table Column Headers
        "col_select": "",
        "col_ip": "IPv4 Address",
        "col_mac": "MAC Address",
        "col_model": "Model",
        "col_type": "Device Type",
        "col_status": "Status",
        "col_port": "Port",
        "col_version": "Software Version",

        # Right Panel
        "panel_title": "Modify Network Parameters",
        "enable_dhcp": "Enable DHCP",
        "enable_hik": "Enable Hik-Connect",
        "field_model": "Device Model:",
        "placeholder_model": "Device model...",
        "tooltip_model": "Detected or custom device model",
        "field_serial": "Device Serial No.:",
        "tooltip_serial": "Serial number is read-only",
        "field_ip": "IP Address:",
        "field_port": "Current SDK Port:",
        "field_sdk_port": "SDK Service Port:",
        "field_subnet": "Subnet Mask:",
        "field_gateway": "Gateway:",
        "field_ipv6": "IPv6 Address:",
        "field_ipv6_gw": "IPv6 Gateway:",
        "field_ipv6_prefix": "IPv6 Prefix Length:",
        "field_http_port": "HTTP Port:",
        "sec_verification": "Security Verification",
        "admin_password": "Administrator Password:",
        "enter_password": "Enter admin password",
        "modify": "Modify",
        "forgot_password": "Forgot Password",

        # Dialogs & Prompts
        "scan_in_progress_title": "Scan in Progress",
        "scan_in_progress_msg": "A scan is already in progress.",
        "no_data_title": "No Data",
        "no_data_msg": "There are no devices to export.",
        "export_dialog_title": "Export Hikvision Device List",
        "csv_filter": "CSV Files (*.csv);;All Files (*)",
        "export_success_title": "Success",
        "export_success_msg": "Data exported successfully ({count} devices) to:\n'{filename}'",
        "export_error_title": "Export Error",
        "export_error_msg": "Error exporting file: {error}",
        
        # Modification & Unbind
        "select_device_title": "Select Device",
        "select_device_msg": "Please select a device from the list first.",
        "password_req_title": "Password Required",
        "password_req_msg": "Please enter the device administrator password to apply changes.",
        "password_unbind_req_msg": "Please enter the administrator password in the security verification field to unbind.",
        "invalid_ip_title": "Invalid IP",
        "invalid_ip_msg": "Please enter a valid IPv4 address (e.g. 192.168.1.64).",
        "invalid_subnet_title": "Invalid Subnet Mask",
        "invalid_subnet_msg": "Please enter a valid subnet mask (e.g. 255.255.255.0).",
        "binary_not_found_title": "Error",
        "binary_not_found_msg": "Executable SADP binary not found for network modification.",
        "modify_success_title": "Modification Successful",
        "modify_success_msg": (
            "<b>Network parameters updated successfully!</b><br><br>"
            "• IPv4 Address: <b>{ip}</b><br>"
            "• Subnet Mask: {subnet}<br>"
            "• Gateway: {gateway}<br>"
            "• DHCP: {dhcp}<br><br>"
            "<i>A new scan will refresh the device list.</i>"
        ),
        "modify_error_title": "Modification Error",
        "confirm_unbind_title": "Confirm Unbind",
        "confirm_unbind_msg": "Are you sure you want to unbind device with MAC <b>{mac}</b> from Hik-Connect / Ezviz?",
        "unbind_success_title": "Unbind Successful",
        "unbind_error_title": "Unbind Error",
        "enabled": "Enabled",
        "disabled": "Disabled",
        "feature_pending": "Not supported yet; this field is not sent to the device.",
        "port_readonly": "Current SDK port. Edit the SDK service port field to change it.",
        "invalid_parameters_title": "Invalid network parameters",
        "invalid_gateway_msg": "Enter a valid gateway in the device subnet, or leave it blank.",
        "invalid_port_msg": "The SDK port must be an integer between 1 and 65535.",
        "invalid_mac_msg": "The selected device does not have a valid MAC address. Scan again.",
        "operation_busy_title": "Operation in progress",
        "operation_busy_msg": "Wait for the current network operation to finish before closing.",
        "command_failed": "The SADP helper failed. The operation was not confirmed. Scan before retrying.",
        "command_no_response": "No acknowledgement received (timeout). Scan before retrying; the device may have applied the command.",
        "command_unconfirmed": "The reply does not confirm this operation. Scan and check the device before retrying.",
        "command_rejected": "The device rejected the operation or returned an unsupported result code.",
        "command_password_error": "The device rejected the administrator password.",
        "command_confirmed": "The device acknowledged the network change.",
        "unbind_success_msg": "The device acknowledged the Hik-Connect/Ezviz unbind command.",
        
        # Forgot Password
        "forgot_password_title": "Restore Password (Forgot Password)",
        "forgot_password_msg": (
            "<b>Local Offline Password Reset</b><br><br>"
            "To restore factory password:<br>"
            "1. Generate a password reset request file (.xml) from the physical camera or SADP utility.<br>"
            "2. Contact official Hikvision support or use the Hik-Partner Pro mobile app to receive an unlock code/file.<br>"
            "3. Import the returned XML response file to reset the administrator password.<br><br>"
            "<i>This offline reset workflow is planned for an upcoming release.</i>"
        ),
    },
    "es": {
        # App & Window
        "app_title": "SADP for Linux",
        "brand_subtitle": "Descubrimiento de equipos Hikvision · por mnxx29",
        "settings": "Ajustes",
        "language": "Idioma",
        "total_devices": "Equipos en línea:",
        "unbind": "Desvincular",
        "export": "Exportar",
        "refresh": "Escanear red",
        "filter": "Filtrar",
        "modify_network": "Configurar red",
        "hide_panel": "Ocultar ajustes",
        
        # Status Messages
        "press_refresh": "Escanea la red para descubrir equipos",
        "scanning": "Escaneando dispositivos... por favor espera",
        "found_devices": "✅ Se encontraron {count} dispositivo(s)",
        "no_devices": "⚠️ No se encontraron dispositivos Hikvision en la red",
        "scan_error": "❌ Error durante el escaneo",
        "opening_browser": "Abriendo {url} en el navegador...",
        "sending_changes": "Enviando cambios de red a {mac} ({new_ip})... por favor espera",
        "unbinding_device": "Desvinculando dispositivo {mac}...",
        "exported": "Exportado: {filename}",

        # Table Column Headers
        "col_select": "",
        "col_ip": "Dirección IP",
        "col_mac": "Dirección MAC",
        "col_model": "Modelo",
        "col_type": "Tipo de Dispositivo",
        "col_status": "Estado",
        "col_port": "Puerto",
        "col_version": "Versión",

        # Right Panel
        "panel_title": "Modificar Parámetros de Red",
        "enable_dhcp": "Habilitar DHCP",
        "enable_hik": "Habilitar Hik-Connect",
        "field_model": "Modelo del equipo:",
        "placeholder_model": "Modelo del dispositivo...",
        "tooltip_model": "Modelo detectado o personalizado del dispositivo",
        "field_serial": "Nº de Serie del Dispositivo:",
        "tooltip_serial": "El número de serie es de sólo lectura",
        "field_ip": "Dirección IP:",
        "field_port": "Puerto SDK actual:",
        "field_sdk_port": "Puerto de servicio SDK:",
        "field_subnet": "Máscara de Subred:",
        "field_gateway": "Puerta de Enlace:",
        "field_ipv6": "Dirección IPv6:",
        "field_ipv6_gw": "Puerta de Enlace IPv6:",
        "field_ipv6_prefix": "Longitud del Prefijo IPv6:",
        "field_http_port": "Puerto HTTP:",
        "sec_verification": "Verificación de Seguridad",
        "admin_password": "Contraseña de Administrador:",
        "enter_password": "Introduce contraseña admin",
        "modify": "Modificar",
        "forgot_password": "Olvidé mi contraseña",

        # Dialogs & Prompts
        "scan_in_progress_title": "Escaneo en curso",
        "scan_in_progress_msg": "Ya hay un escaneo en progreso.",
        "no_data_title": "No hay datos",
        "no_data_msg": "No hay dispositivos para exportar.",
        "export_dialog_title": "Exportar lista de dispositivos Hikvision",
        "csv_filter": "Archivos CSV (*.csv);;Todos los archivos (*)",
        "export_success_title": "Éxito",
        "export_success_msg": "Datos exportados exitosamente ({count} dispositivos) a:\n'{filename}'",
        "export_error_title": "Error al exportar",
        "export_error_msg": "Error al exportar: {error}",
        
        # Modification & Unbind
        "select_device_title": "Seleccionar Dispositivo",
        "select_device_msg": "Por favor, selecciona primero un dispositivo de la lista.",
        "password_req_title": "Contraseña Requerida",
        "password_req_msg": "Por favor, introduce la contraseña de administrador del dispositivo para aplicar los cambios.",
        "password_unbind_req_msg": "Por favor, introduce la contraseña de administrador en el campo de verificación para desvincular.",
        "invalid_ip_title": "IP Inválida",
        "invalid_ip_msg": "Por favor, introduce una dirección IPv4 válida (ej. 192.168.1.64).",
        "invalid_subnet_title": "Máscara Inválida",
        "invalid_subnet_msg": "Por favor, introduce una máscara de subred válida (ej. 255.255.255.0).",
        "binary_not_found_title": "Error",
        "binary_not_found_msg": "No se encontró el binario SADP ejecutable para enviar la modificación.",
        "modify_success_title": "Modificación Exitosa",
        "modify_success_msg": (
            "<b>¡Parámetros de red actualizados correctamente!</b><br><br>"
            "• Dirección IP: <b>{ip}</b><br>"
            "• Máscara de subred: {subnet}<br>"
            "• Puerta de enlace: {gateway}<br>"
            "• Estado DHCP: {dhcp}<br><br>"
            "<i>Se iniciará un nuevo escaneo de red para refrescar la lista.</i>"
        ),
        "modify_error_title": "Error de Modificación",
        "confirm_unbind_title": "Confirmar Desvinculación",
        "confirm_unbind_msg": "¿Estás seguro de que deseas desvincular de Hik-Connect/Ezviz el dispositivo con MAC <b>{mac}</b>?",
        "unbind_success_title": "Desvinculación Exitosa",
        "unbind_error_title": "Error al Desvincular",
        "enabled": "Habilitado",
        "disabled": "Deshabilitado",
        "feature_pending": "Todavía no compatible; este campo no se envía al dispositivo.",
        "port_readonly": "Puerto SDK actual. Para cambiarlo, edita el campo de servicio SDK.",
        "invalid_parameters_title": "Parámetros de red inválidos",
        "invalid_gateway_msg": "Introduce una puerta de enlace válida de la subred del dispositivo o deja el campo vacío.",
        "invalid_port_msg": "El puerto SDK debe ser un entero entre 1 y 65535.",
        "invalid_mac_msg": "El dispositivo seleccionado no tiene una MAC válida. Repite el escaneo.",
        "operation_busy_title": "Operación en curso",
        "operation_busy_msg": "Espera a que termine la operación de red antes de cerrar.",
        "command_failed": "El auxiliar SADP falló. La operación no está confirmada. Escanea antes de reintentar.",
        "command_no_response": "No se recibió confirmación (timeout). Escanea antes de reintentar; el dispositivo podría haber aplicado la orden.",
        "command_unconfirmed": "La respuesta no confirma esta operación. Escanea y comprueba el dispositivo antes de reintentar.",
        "command_rejected": "El dispositivo rechazó la operación o devolvió un código de resultado no compatible.",
        "command_password_error": "El dispositivo rechazó la contraseña de administrador.",
        "command_confirmed": "El dispositivo confirmó el cambio de red.",
        "unbind_success_msg": "El dispositivo confirmó la orden de desvinculación de Hik-Connect/Ezviz.",
        
        # Forgot Password
        "forgot_password_title": "Restaurar Contraseña (Forgot Password)",
        "forgot_password_msg": (
            "<b>Restablecimiento de Contraseña Local Offline</b><br><br>"
            "Para restaurar la contraseña de fábrica:<br>"
            "1. Genera un archivo XML de solicitud (.xml) desde la cámara física o su utilidad.<br>"
            "2. Contacta al soporte oficial de Hikvision o utiliza la app Hik-Partner Pro para obtener un código de desbloqueo.<br>"
            "3. Importa el archivo XML de respuesta recibido para actualizar la contraseña del administrador.<br><br>"
            "<i>Esta herramienta modularizará el soporte offline en próximas compilaciones.</i>"
        ),
    }
}

DEVICE_TYPE_NAMES = {
    "ipc": {"en": "IP Camera", "es": "Cámara IP"},
    "ptz": {"en": "PTZ Camera", "es": "Cámara PTZ"},
    "nvr": {"en": "NVR", "es": "NVR"},
    "dvr": {"en": "DVR", "es": "DVR"},
    "intercom": {"en": "Video Intercom", "es": "Videoportero"},
    "switch": {"en": "PoE Switch", "es": "Switch PoE"},
    "device": {"en": "Device", "es": "Dispositivo"},
}

MAPA_CODIGOS_TIPO = {
    # Cámaras IP (DS-2CD...)
    "141938": "ipc",
    "147479": "ipc",
    "141904": "ipc",
    "141937": "ipc",
    "141939": "ipc",
    "141950": "ipc",
    "147456": "ipc",
    # Cámaras PTZ / Speed Dome (DS-2SE, DS-2DE...)
    "196607": "ptz",
    "196608": "ptz",
    "196609": "ptz",
    # NVR (DS-96, DS-76...)
    "46877": "nvr",
    "46848": "nvr",
    "46849": "nvr",
    "46876": "nvr",
    "46878": "nvr",
    # DVR (DS-72, DS-71...)
    "42240": "dvr",
    "42241": "dvr",
    "42242": "dvr",
    # Videoporteros / Control de Acceso
    "262144": "intercom",
    "262145": "intercom",
    # Switches PoE
    "393216": "switch",
}


def t(key: str, lang: str = "en", **kwargs) -> str:
    """Returns the localized string for `key` in `lang`, falling back to English."""
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    text = lang_dict.get(key, TRANSLATIONS["en"].get(key, key))
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text


def translate_device_type(tipo_code: str, serial_model: str = "", lang: str = "en") -> str:
    """Translates Hikvision numeric SADP codes and model prefixes into localized names."""
    tipo_str = str(tipo_code).strip()
    model_upper = str(serial_model).upper()

    # 1. Known numeric code mapping
    if tipo_str in MAPA_CODIGOS_TIPO:
        cat = MAPA_CODIGOS_TIPO[tipo_str]
        label = DEVICE_TYPE_NAMES[cat].get(lang, DEVICE_TYPE_NAMES[cat]["en"])
        return f"{label} ({tipo_str})"

    # 2. Smart prefix inference
    cat = ""
    if any(p in model_upper for p in ("DS-2SE", "DS-2DE", "DS-2DF", "PTZ")):
        cat = "ptz"
    elif any(p in model_upper for p in ("DS-2CD", "DS-2CV", "IPC")):
        cat = "ipc"
    elif any(p in model_upper for p in ("DS-96", "DS-76", "DS-77", "NVR")):
        cat = "nvr"
    elif any(p in model_upper for p in ("DS-71", "DS-72", "DS-73", "DVR")):
        cat = "dvr"
    elif any(p in model_upper for p in ("DS-KD", "DS-KV", "DS-KH")):
        cat = "intercom"
    elif "DS-3E" in model_upper:
        cat = "switch"
    elif tipo_str.isdigit():
        cat = "device"

    if cat:
        label = DEVICE_TYPE_NAMES.get(cat, {}).get(lang, DEVICE_TYPE_NAMES.get(cat, {}).get("en", "Device"))
        return f"{label} ({tipo_str})" if tipo_str.isdigit() else label

    default_device = "Device" if lang == "en" else "Dispositivo"
    return tipo_str if tipo_str else default_device


# Backward compatibility alias
traducir_tipo_dispositivo = translate_device_type
