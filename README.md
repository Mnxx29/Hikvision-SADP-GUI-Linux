# Hikvision SADP Tool for Linux (GUI)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-PyQt6-green.svg)](https://riverbankcomputing.com/software/pyqt/)
[![Platform](https://img.shields.io/badge/Platform-Linux%20(Ubuntu%20%7C%20Debian)-orange.svg)](https://ubuntu.com/)
[![Protocol](https://img.shields.io/badge/Protocol-SADP%20(UDP%2037020)-red.svg)](#architecture-and-features)

**English** | [Español](README_es.md)

> A full-featured, native Linux graphical interface (GUI) alternative to Hikvision's official Windows-only SADP Tool. Discover, configure, and manage Hikvision IP cameras, NVRs, DVRs, and intercoms on your local network.

---

## Overview

Hikvision does not provide an official native **SADP (Search Active Devices Protocol)** application for Linux. While command-line scripts exist, network technicians, sysadmins, and CCTV installers often need a visual, fast, and intuitive desktop interface to manage devices on field installations.

**Hikvision SADP GUI Linux** solves this by delivering a native PyQt6 desktop application designed specifically for Linux. It directly implements the SADP protocol to scan across multiple network interfaces, detect devices even on different subnets, configure IP addresses, and unbind devices from Hik-Connect accounts.

<p align="center">
  <img src="docs/GUI.png" alt="Hikvision SADP Linux GUI Screenshot" width="850">
</p>

---

## Comparison: Official SADP vs. CLI Tools vs. This Project

| Feature | Official Hikvision SADP | CLI Tools (`hikvision-tooling`) | **Hikvision SADP GUI Linux (This Repo)** |
| :--- | :---: | :---: | :---: |
| **Linux Native** | ❌ (Windows only / Broken under Wine) | ✅ | ✅ **Yes** |
| **User Interface** | ✅ Windows GUI | ❌ CLI only | ✅ **PyQt6 Modern GUI** |
| **SADP Discovery (UDP 37020)** | ✅ | ✅ | ✅ **Simultaneous Multicast & Broadcast** |
| **Cross-Subnet Discovery** | ⚠️ Inconsistent | ❌ | ✅ **Full Support (`rp_filter=2`)** |
| **Multi-NIC & VLAN Scanning** | ⚠️ Single active adapter | ❌ | ✅ **All active interfaces probed** |
| **Modify Network Parameters (IP, Mask, GW)** | ✅ | ⚠️ Complex flags | 🚧 *In active development (Coming in next release)* |
| **Hik-Connect Unbind** | ✅ | ❌ | 🚧 *In active development* |
| **Device Model & Type Translation** | ✅ | ⚠️ Raw codes | ✅ **Automatic (Camera, PTZ, NVR, DVR)** |
| **CSV Export** | ✅ | ❌ (JSON stdout only) | ✅ **Full CSV Report Generation** |
| **Built-in Network Diagnostics** | ❌ | ❌ | ✅ **Integrated Diagnostic Script** |

---

## Key Features

- **Native Protocol Implementation**: Sends and listens directly on UDP port `37020` via multicast (`239.255.255.250`) and local broadcast.
- **Cross-Subnet & Factory Default Detection**: Finds brand new or unconfigured cameras (default IP `192.168.1.64`) even if your Linux workstation is in a completely different subnet (e.g. `10.0.0.0/24` or `172.16.0.0/16`).
- **Simultaneous Multi-Interface Scanning**: Discovers equipment connected across multiple Ethernet adapters, Wi-Fi, and tagged VLANs simultaneously.
- **Device Model & Type Identification**: Recognizes and labels Hikvision hardware codes (`IP Camera`, `PTZ Camera`, `NVR`, `DVR`, `Video Intercom`, `PoE Switch`).
- **Complete CSV Export**: Generate audit reports with all discovered parameters: IP, MAC address, device type, software version, serial number, ports, and DHCP status.
- **Diagnostic Toolkit**: Includes [`diagnostico.sh`](diagnostico.sh) to test firewall rules (UFW/iptables), multicast routing, socket binding, and raw packet capture.
- **Linux Desktop Integration**: Automatically installs a system launcher command (`sadp-gui`) and an application shortcut (`.desktop`) in your desktop menu.

> 🚧 **Upcoming Features (Roadmap)**:
> - Direct network parameter modification (IP, Subnet Mask, Gateway, DHCP) from the right-hand panel.
> - Direct Hik-Connect account unbind feature.

---

## System Requirements

- **Operating System**: Ubuntu 20.04 LTS / 22.04 LTS / 24.04 LTS, Debian 11 / 12, Linux Mint, or other Debian-based distributions.
- **Python**: Version 3.8 or higher with `PyQt6`.
- **Go**: Required during setup to build the high-speed network modification binary.
- **Network**: Active Ethernet/Wi-Fi adapter connected to the same physical or virtual switch as the Hikvision devices.

---

## Installation

Clone the repository and run the automated production setup script:

```bash
# Clone the repository
git clone https://github.com/Mnxx29/Hikvision-SADP-GUI-Linux.git
cd Hikvision-SADP-GUI-Linux

# Run the installer (do not run with sudo)
bash setup-produccion.sh
```

> **Note**: Run the script as your regular user. The installer will ask for `sudo` privileges only when configuring necessary kernel parameters, firewall permissions, and system packages.

### Launching the Application

Once installed, launch the application from your terminal:

```bash
sadp-gui
```

Or search for **"Hikvision SADP"** in your desktop application menu (GNOME, KDE Plasma, XFCE, etc.).

---

## Network Troubleshooting & Diagnostics

If your Linux firewall (UFW) blocks UDP traffic or your system does not receive multicast responses:

```bash
bash diagnostico.sh
```

This diagnostic script automatically verifies:
1. UDP port `37020` socket availability.
2. Reverse path filtering (`rp_filter`) settings for cross-subnet discovery.
3. UFW and iptables firewall rules for multicast traffic.
4. Interface link status and IP addressing.

For an in-depth protocol breakdown and manual network setup, refer to the [Technical Guide (GUIA.md)](GUIA.md).

---

## Contributing

Contributions, bug reports, and feature requests are welcome!
Check out the [Contributing Guidelines](CONTRIBUTING.md) to get started, report an issue, or submit a pull request.

---

## Frequently Asked Questions (FAQ)

### Is there an official Hikvision SADP tool for Linux?
No. Hikvision only provides the official SADP (Search Active Devices Protocol) software for Microsoft Windows. This project was developed from scratch to offer a native Linux equivalent with an intuitive desktop GUI.

### Can I run Hikvision SADP on Linux without Wine or Virtual Machines?
Yes! This application runs natively on Linux using Python 3 and PyQt6. It connects directly to raw UDP multicast sockets (`239.255.255.250:37020`), eliminating the need for Wine, emulators, or Windows virtual machines.

### How does cross-subnet discovery work for unconfigured cameras (192.168.1.64)?
Brand-new Hikvision devices default to the `192.168.1.64` IP address. Linux kernels typically drop asymmetric packets from other subnets by default. The setup script adjusts reverse path filtering (`rp_filter=2`) and binds route paths across all network interfaces, allowing SADP multicast probes and responses to cross subnet boundaries seamlessly.

### Which Linux distributions are supported?
The tool is fully tested on Ubuntu (20.04 LTS, 22.04 LTS, 24.04 LTS), Debian (11 / 12), Linux Mint, and other Debian-based operating systems. It also runs on Arch Linux, Fedora, and openSUSE with `python3-pyqt6` installed.

### Does this tool work with OEM Hikvision equipment?
Yes. Many brands (such as Annke, LTS, Lorex, Swann, and others) use Hikvision OEM hardware and firmware. If the device communicates over port 37020 using the SADP protocol, this tool will detect and list it.

---

## Disclaimer

This is an independent open-source community project. It is **not** affiliated with, sponsored by, authorized by, or endorsed by **Hangzhou Hikvision Digital Technology Co., Ltd.**

"Hikvision", "EZVIZ", "Hik-Connect", and "SADP" are registered trademarks of their respective owners. All product names, logos, and brands are used for identification and interoperability purposes only under fair use.

---

## License

This project is open-source software licensed under the [MIT License](LICENSE).

