# Validation — 1.0.5

Test date: **2026-10-27**. Ubuntu Desktop 24.04.5 LTS amd64 in the existing VirtualBox test VM. This report describes validation before publication; GitHub Actions tests and builds the tagged source separately.

- All **43 automated tests passed** with `/usr/bin/python3 -m unittest discover -s tests -v` and Qt's offscreen platform. New tests cover per-device worker signals before the final list, deduplication of two MAC formats, incremental table updates with an active filter, and direct browser opening without a confirmation dialog.
- A native SADP scan on the VM's connected network found **35 devices**. The first table row appeared after **0.06 s**; all 35 were visible by **0.59 s**; the scan finished after **12.1 s**. The count rose during the scan. These timings are observations from this VM and network, not latency guarantees.
- Calling the GUI's IP double-click handler in the Ubuntu desktop session for a known device opened the VM's default Chrome browser with its HTTP address. No confirmation dialog appeared. The test did not log in to or change the device.
- Discovery probes and the browser opening did not change device configuration. The test did not exercise network modification or unbind. A prior real-camera modification attempt timed out without a matching acknowledgement; those operations remain unverified on that camera.

The test source and raw timing logs are kept outside the published package. The base Ubuntu snapshot is intact.
