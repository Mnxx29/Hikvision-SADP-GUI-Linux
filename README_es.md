# Hikvision SADP GUI para Linux

[English](README.md) | **Español**

Descubrimiento nativo de dispositivos compatibles con Hikvision mediante Python y PyQt6. La interfaz permite filtrar y ordenar resultados, guardar etiquetas de modelo locales y exportar CSV con números de serie.

![Aplicación](docs/GUI.png)

La interfaz usa una identidad propia en carbón y rojo. Cambia el idioma desde `⋯ → Idioma`; la elección se guarda automáticamente.

## Requisitos y validación

- Python **3.9+**, PyQt6 **6.4+**, Linux con IPv4 e `iproute2`.
- El auxiliar incluido en los paquetes es **Linux amd64**. Otras arquitecturas requieren compilar su propio auxiliar.
- El entorno de pruebas es **Ubuntu Desktop 24.04 LTS amd64**. Debian 12 y otras distribuciones no están certificadas por las pruebas de esta VM.
- Los dispositivos deben compartir un segmento de capa 2 alcanzable por alguna interfaz escaneada. Pueden tener IP de otra subred en ese segmento; esto no atraviesa automáticamente routers ni límites de VLAN.
- Para compilar: Git, `dpkg-dev` y Go **1.21+** como arranque. La compilación descarga y utiliza la versión exacta indicada en [packaging/upstream.env](packaging/upstream.env). Los paquetes de release no necesitan Go para ejecutarse.

## Instalación

Descarga el `.deb` desde [Releases](https://github.com/Mnxx29/Hikvision-SADP-GUI-Linux/releases):

```bash
sudo apt install ./hikvision-sadp-gui_1.0.4_amd64.deb
sadp-gui
```

Verifica las descargas con el archivo `SHA256SUMS.txt` incluido en cada release.

La aplicación se instala en `/opt/hikvision-sadp`, con el comando `/usr/bin/sadp-gui` y acceso en el menú. Ejecuta la GUI como usuario normal.

Para el tarball, instala primero Python/PyQt6 y las dependencias de red con el gestor de tu distribución. Extrae el archivo y ejecuta `sudo bash install.sh`. No mezcles una instalación tarball con el paquete Debian. Para quitarla, usa `sudo bash uninstall.sh` del mismo paquete.

### Desde código fuente (Debian/Ubuntu)

```bash
git clone https://github.com/Mnxx29/Hikvision-SADP-GUI-Linux.git
cd Hikvision-SADP-GUI-Linux
bash setup-produccion.sh
```

El script compila el auxiliar fijado e instala el mismo paquete Debian, usando sudo para la instalación. Retira los lanzadores antiguos de usuario que ocultarían el comando del sistema. Después de migrar puedes quitar `~/.local/bin/sadp` con `clean-install.sh`.

## Permisos de red y desinstalación

La instalación requiere root; abrir y escanear no. La versión 1.0.3 retira `/etc/sudoers.d/sadp-gui-routing` de 1.0.2 y no crea reglas sudoers sin contraseña ni capabilities de sockets raw.

El instalador configura únicamente `net.ipv4.conf.all.rp_filter=2` y `net.ipv4.conf.default.rp_filter=2` en `/etc/sysctl.d/60-hikvision-sadp.conf`. Guarda los valores previos en `/var/lib/hikvision-sadp/network-state.json` y los conserva al actualizar. Estos ajustes de filtrado de ruta inversa afectan al sistema completo y permiten respuestas asimétricas conservando la validación de ruta en modo laxo.

Si UFW ya está activo y no existe una política SADP, añade reglas SADP para UDP con destino 37020, respuestas desde el puerto 37020 (el auxiliar usa puertos locales efímeros) y multicast de salida a `239.255.255.250:37020`. **Nunca activa UFW**. Respeta las reglas SADP previas del administrador sin cambiar su etiqueta ni ampliarlas; en ese caso solicita revisar esa política. Si lo activas después, ejecuta explícitamente `sudo python3 /opt/hikvision-sadp/network_setup.py configure`. Otros firewalls requieren configuración equivalente del administrador.

```bash
sudo apt remove hikvision-sadp-gui
```

La desinstalación restaura los valores del kernel si todavía coinciden con lo aplicado, elimina su archivo sysctl sin modificaciones y retira solo las reglas UFW añadidas por esta versión. Respeta cambios posteriores del administrador. Conserva las reglas heredadas de 1.0.2 porque esa versión no registraba su propietario; puedes revisarlas con `sudo ufw show added`.

## Funciones y límites

El descubrimiento usa [sadp_discover.py](sadp_discover.py). El auxiliar Go revisado gestiona cambios de red y desvinculación Hik-Connect/Ezviz. Su commit y compilador están fijados; los paquetes incluyen su licencia MIT.

- Campos de modificación admitidos: IPv4, máscara contigua en notación decimal, gateway, puerto SDK y DHCP.
- HTTP, IPv6 y habilitación de Hik-Connect quedan deshabilitados. El modelo editable es una etiqueta local, no una configuración del dispositivo.
- Solo se anuncia éxito con código de salida cero y confirmación SADP explícita del dispositivo seleccionado. Respuestas desconocidas y timeouts quedan **sin confirmar**: escanea y comprueba el equipo antes de reintentar. No se reenvían automáticamente órdenes de modificación.
- Los cambios de red y la desvinculación necesitan validación independiente con hardware. Detectar equipos no certifica esas operaciones ni todos los códigos de firmware.
- La recuperación de contraseña no está implementada; la GUI explica el procedimiento externo de soporte.

## Diagnóstico y desarrollo

```bash
bash diagnostico.sh
python3 sadp_discover.py --timeout 6 --debug
python3 sadp_discover.py --timeout 6 --csv > devices.csv
```

El diagnóstico inspecciona la configuración y envía sondas de descubrimiento; no modifica rutas, firewall ni kernel. La salida CSV es procesable directamente; con `--csv`, la depuración va a stderr.

Consulta [CONTRIBUTING.md](CONTRIBUTING.md), [CHANGELOG.md](CHANGELOG.md) y las [notas de validación](docs/validation-1.0.3.md).

## Descargo y licencia

Proyecto comunitario independiente, sin afiliación ni respaldo de Hikvision. Hikvision, EZVIZ, Hik-Connect y SADP pertenecen a sus respectivos propietarios y se utilizan para identificar equipos compatibles.

Código de la GUI: [MIT](LICENSE). El auxiliar `hikvision-tooling` incluye su propia licencia y aviso de copyright MIT.
