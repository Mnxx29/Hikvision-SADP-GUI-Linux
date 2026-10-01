# Hikvision SADP GUI para Linux

[English](README.md) | **Español**

Aplicación gráfica nativa para Linux para el descubrimiento, diagnóstico y gestión de red de cámaras IP y dispositivos Hikvision en redes locales y subredes múltiples.

<p align="center">
  <img src="docs/GUI.png" alt="Captura de pantalla SADP Tool para Linux" width="850">
</p>

## Instalación

```bash
bash setup-produccion.sh
```

Ejecutar sin `sudo`. El instalador solicitará privilegios de superusuario únicamente cuando sea necesario para la configuración de red y dependencias.

Para ejecutar la aplicación después de instalar:

```bash
sadp-gui
```

## Requisitos del sistema

- Ubuntu 20.04 LTS o superior (o distribuciones basadas en Debian/Ubuntu).
- Python 3.8+ con `PyQt6`.
- Go (requerido para la compilación del binario auxiliar de modificaciones de red).
- Interfaz de red activa conectada al segmento o VLAN de los dispositivos.

## Arquitectura y características técnicas

- **Motor de descubrimiento nativo (Python)**: Implementación directa del protocolo SADP vía UDP multicast (`239.255.255.250:37020`) y broadcast, enlazada directamente al puerto 37020 para garantizar la recepción de respuestas a través de reglas de firewall.
- **Soporte multi-interfaz y VLAN**: Envío de sondas en todas las interfaces de red activas de forma simultánea.
- **Soporte fuera de subred**: Detección de dispositivos sin importar si se encuentran en un segmento IP distinto al del equipo local, mediante configuración del kernel (`rp_filter=2`).
- **Traducción de tipo de dispositivo**: Identificación de códigos numéricos SADP y prefijos de modelo (`Cámara IP`, `Cámara PTZ`, `NVR`, `DVR`, `Videoportero`, `Switch PoE`).
- **Exportación CSV completa**: Generación de reportes CSV estructurados con la totalidad de atributos de red detectados (`ip`, `mac`, `tipo`, `estado`, `puerto`, `http_port`, `serial`, `version`, `subnet`, `gateway`, `dhcp`).
- **Herramienta de diagnóstico integrada**: Script `diagnostico.sh` para auditoría de sockets, reglas UFW, permisos `cap_net_raw`, capturas `tcpdump` y pruebas del protocolo.

> 🚧 **Próximas funciones (En desarrollo activo)**:
> - Modificación de parámetros de red (IP, máscara, puerta de enlace, DHCP) desde el panel lateral derecho de la aplicación.
> - Desvinculación de cuentas Hik-Connect (Unbind).

## Integración con el sistema

El instalador genera el comando global `sadp-gui` en `~/.local/bin/` y crea el archivo de escritorio `~/.local/share/applications/sadp-gui.desktop` para integración directa en el menú de aplicaciones.

## Documentación detallada

Consulte la [Guía Técnica de Uso y Red](GUIA.md) para especificaciones del protocolo, troubleshooting y configuración avanzada.

## Contribuciones y Feedback

¡Los reportes de errores, sugerencias y contribuciones son bienvenidos!
Si encuentras algún problema o tienes alguna idea de mejora, abre un *Issue* o envía un *Pull Request* en [GitHub](https://github.com/Mnxx29/Hikvision-SADP-GUI-Linux).

---

## Preguntas Frecuentes (FAQ)

### ¿Existe una versión oficial de SADP para Linux?
No. Hikvision únicamente ofrece el software oficial SADP (Search Active Devices Protocol) para Microsoft Windows. Este proyecto fue desarrollado de forma comunitaria e independiente para brindar una alternativa gráfica nativa y completa para Linux.

### ¿Puedo ejecutar SADP en Linux sin Wine ni máquinas virtuales?
¡Sí! Esta aplicación corre de manera 100% nativa sobre Linux utilizando Python 3 y PyQt6. Se conecta directamente a los sockets UDP multicast (`239.255.255.250:37020`), eliminando la necesidad de Wine, emuladores o máquinas virtuales de Windows.

### ¿Cómo detecta cámaras sin configurar en subredes distintas (192.168.1.64)?
Los dispositivos nuevos de Hikvision vienen de fábrica con la IP `192.168.1.64`. Por defecto, el kernel de Linux descarta paquetes asimétricos provenientes de otras subredes. El instalador configura el filtrado de ruta inversa (`rp_filter=2`) y rutas multicast en todas las interfaces de red para que las respuestas SADP atraviesen subredes sin inconvenientes.

### ¿Qué distribuciones de Linux son compatibles?
Probado y verificado en Ubuntu (20.04 LTS, 22.04 LTS, 24.04 LTS), Debian (11 y 12), Linux Mint y derivados. También es compatible con Arch Linux, Fedora y openSUSE con `python3-pyqt6` instalado.

### ¿Funciona con dispositivos OEM de Hikvision?
Sí. Marcas como Annke, LTS, Lorex y otras utilizan hardware y firmware OEM de Hikvision. Si el dispositivo responde al protocolo SADP por el puerto 37020, esta aplicación lo detectará e identificará.

---

## Descargo de Responsabilidad (Disclaimer)

Este es un proyecto de código abierto independiente desarrollado por la comunidad. **No** está afiliado, patrocinado, autorizado ni respaldado por **Hangzhou Hikvision Digital Technology Co., Ltd.**

"Hikvision", "EZVIZ", "Hik-Connect" y "SADP" son marcas comerciales registradas de sus respectivos propietarios. Todos los nombres de productos, marcas y logotipos se utilizan exclusivamente con fines de identificación y compatibilidad técnica bajo el principio de uso legítimo (*Fair Use*).

---

## Licencia

MIT License — consulte el archivo [LICENSE](LICENSE) para más detalles.

