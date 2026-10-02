# Contributing to Hikvision SADP GUI for Linux

Thank you for considering contributing to **Hikvision SADP GUI for Linux**! Community contributions, bug reports, and device compatibility tests help make this tool better for network administrators and security installers worldwide.

---

## How Can I Contribute?

### 1. Reporting Bugs
Before creating a bug report, please check existing [Issues](https://github.com/Mnxx29/Hikvision-SADP-GUI-Linux/issues) to avoid duplicates. When opening an issue, please include:
- **Operating System & Version** (e.g., Ubuntu 24.04 LTS, Debian 12, Fedora 40, Arch Linux).
- **Desktop Environment** (e.g., GNOME, KDE Plasma, XFCE).
- **Network Setup** (Ethernet interface, Wi-Fi, VLAN, switch model).
- **Device Model(s)** (e.g., DS-2CD2143G0-I, DS-7608NI-K2).
- **Diagnostic Output**: Run `./diagnostico.sh` and attach the output or relevant terminal logs.

### 2. Suggesting Features & Enhancements
Feature requests are welcome! Please open an issue describing:
- The problem you are trying to solve.
- Your proposed solution or desired behavior.
- Any relevant Hikvision device behaviors, protocols, or packet samples.

### 3. Adding or Improving Translations
We support internationalization via [i18n.py](file:///c:/Users/Omnifish/Desktop/Repositorios/hikvision-sadp-gui-linux/i18n.py):
- English (`en`) is the default fallback language.
- Spanish (`es`) is fully supported.
- If you would like to add support for another language (e.g., French, German, Portuguese, Italian, Chinese), add a new dictionary under `TRANSLATIONS` in `i18n.py` and submit a Pull Request!

---

## Local Development Setup

### Prerequisites
Make sure you have Python 3.9+ and pip installed on your Linux system:

```bash
# Ubuntu / Debian
sudo apt update && sudo apt install -y python3 python3-pip python3-pyqt6

# Fedora
sudo dnf install -y python3 python3-pip python3-pyqt6

# Arch Linux
sudo pacman -S python python-pip python-pyqt6
```

### Running from Source
1. Fork and clone the repository:
   ```bash
   git clone https://github.com/Mnxx29/Hikvision-SADP-GUI-Linux.git
   cd Hikvision-SADP-GUI-Linux
   ```
2. Install required Python packages:
   ```bash
   pip3 install -r requirements.txt # or pip3 install PyQt6 netifaces
   ```
3. Run the application:
   ```bash
   python3 gui_sadp.py
   ```

---

## Pull Request Guidelines

1. **Create a Feature Branch**: Work on a branch with a descriptive name (e.g., `feat/add-french-language` or `fix/discovery-vlan-bind`).
2. **Preserve Internationalization**: If you introduce new UI text, always wrap it with `t("key")` and define the key in [i18n.py](file:///c:/Users/Omnifish/Desktop/Repositorios/hikvision-sadp-gui-linux/i18n.py).
3. **Keep English as Default**: Ensure default strings and fallbacks remain in English.
4. **Test Clean Execution**: Ensure the app runs without uncaught exceptions:
   ```bash
   python3 -m py_compile gui_sadp.py i18n.py sadp_discover.py
   ```
5. **Submit your PR**: Describe what was changed, why, and how it was tested.

Thank you for helping improve open-source tools for Linux!
