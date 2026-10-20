# 1.0.3 — installation permissions and reliable operation results

SADP starts and scans as a normal user. Installation removes the broad passwordless sudoers rules used by 1.0.2, configures only SADP network settings, and never enables an inactive firewall. Uninstallation restores tracked settings and removes only firewall rules added by this version. Existing 1.0.2 firewall rules are preserved because their ownership was not recorded.

Network changes and Hik-Connect unbind now require a successful helper exit and an explicit acknowledgement from the selected device. Unknown replies and timeouts remain unconfirmed; check the device before retrying. The UI validates network parameters and disables unsupported fields. CSV exports include serial numbers.

The Go source and toolchain are pinned. Automated parser, validation, GUI and installer tests run before release builds. See the [changelog](https://github.com/Mnxx29/Hikvision-SADP-GUI-Linux/blob/v1.0.3/CHANGELOG.md) and [validation report](https://github.com/Mnxx29/Hikvision-SADP-GUI-Linux/blob/v1.0.3/docs/validation-1.0.3.md) for validation and remaining limits. Real-device IP changes and unbind require separate hardware validation; discovery tests do not certify those operations.

For older per-user source installations, run the updated `setup-produccion.sh` to retire the old user launcher and desktop entry. Installing a system `.deb` does not modify every user home directory.
