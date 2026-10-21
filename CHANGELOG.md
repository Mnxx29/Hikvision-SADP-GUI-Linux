# Changelog

## 1.0.4 — 2026-10-21

- Introduce a charcoal and red workspace with a branded header, separate device actions and alternating table rows.
- Remove the icon's white exterior and supply transparent icons for launchers and windows.
- Move English/Spanish selection into the settings menu, with complete language names and the saved preference retained.
- Keep translated buttons at their required width and preserve readable table columns with horizontal scrolling beside the network panel.
- Set Qt's desktop identity to match the launcher, including Wayland app ID and X11 startup class.
- Install themed icons and refresh icon caches for tarball installations too.

## 1.0.3 — 2026-10-20

- Remove passwordless sudoers and privileged commands from launch and scanning.
- Configure only SADP network settings at installation; retain their original values across upgrades and restore owned settings on removal.
- Never activate UFW automatically; track new SADP rules and preserve existing rules.
- Require an explicit, matching device acknowledgement and a successful helper exit before reporting success. Do not automatically resend uncertain changes.
- Validate IPv4, contiguous netmasks, gateways, MAC addresses and SDK ports.
- Disable unsupported HTTP/IPv6/Hik-Connect settings; retain DHCP field state when selecting a device.
- Include device serial numbers in CSV reports; properly quote CLI CSV output.
- Prevent editing discovered device identities and closing during active network operations.
- Pin the Go helper commit and Go toolchain, include its license, and run tests before packaging a release.
- Align installation paths and document tested compatibility and remaining hardware validation.
