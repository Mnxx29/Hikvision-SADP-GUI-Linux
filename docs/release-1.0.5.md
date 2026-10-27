# 1.0.5 — devices appear as they respond

SADP for Linux now lists devices during the scan. Each newly discovered MAC appears as soon as its response is processed, the online count updates immediately, and the active filter also applies to incoming rows. The scan continues for its normal discovery window to catch slower devices; repeat responses do not add duplicate rows.

Double-clicking a device's IPv4 address now opens its web interface in the system's default browser immediately. The confirmation dialog has been removed.

On the Ubuntu 24.04 test VM, all 43 automated tests passed. A scan on the connected network showed its first device at 0.06 seconds, all 35 detected devices by 0.59 seconds, and completed at 12.1 seconds. The direct browser action launched the VM's default Chrome browser. See the [1.0.5 validation report](https://github.com/Mnxx29/Hikvision-SADP-GUI-Linux/blob/v1.0.5/docs/validation-1.0.5.md).

This release changes discovery presentation and browser opening. Device network modification and unbind compatibility are still limited as described in the validation report.
