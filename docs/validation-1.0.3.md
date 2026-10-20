# Validation — 1.0.3

VM test date: **2026-10-20**. These results describe the local validation performed before publication. GitHub Actions run results are recorded separately in the repository's Actions history.

## Environment

Ubuntu Desktop 24.04.5 LTS amd64 in Oracle VirtualBox 7.2.20, bridged Ethernet, 2 virtual CPUs and 8 GB RAM. Python 3.12, PyQt6 6.6.1 / Qt 6.4.2. The auxiliary executable is built from `afa00e3db11bb47914e1f0d724c6975e0a41e218` using Go 1.26.5.

A powered-off Ubuntu snapshot was restored for the clean-install tests. It contained SSH and Guest Additions, but no Git, SADP package, SADP sysctl file or SADP sudoers file. Live snapshots were unreliable in this VM; no live snapshot is needed to reproduce these tests.

## Results

| Check | Result |
| --- | --- |
| Parser, validation, Qt GUI, workers and network-setting tests | 36 tests passed on Ubuntu, including offscreen GUI tests |
| Shell scripts, launcher and Debian maintainer script syntax | Passed |
| Native GUI scan | 35 real devices, 35 table rows, scan/export controls enabled after completion |
| Native discovery with UFW active | 35 real devices |
| Go discovery without raw-socket capability, with UFW active | 35 real devices |
| GUI fallback against the real Go XML output | 35 devices; full serial numbers retained |
| CSV output from tarball installation | 35 rows; machine-readable header, no progress banner in stdout |
| Clean Debian installation after restoring Ubuntu base | Passed; dependencies resolved by APT |
| Upgrade from the original, checksum-verified 1.0.2 Debian release | Passed; legacy sudoers removed, executable capability removed, legacy firewall policy preserved |
| Remove/purge | Passed; owned config/state removed, original kernel values restored, administrator firewall rules preserved |
| Tarball install/uninstall | Passed; launcher installed/removed, kernel values and administrator firewall policy restored |
| Repeated builds from identical source | Debian and tarball SHA-256 values matched in two independent builds |

The installer was tested with UFW already active. SSH and an unrelated administrator rule were added by the test harness before installation. SADP added its three rules, recorded ownership, and removed them on uninstall while preserving the administrator rules. The deliberately chosen pre-install `rp_filter=1` values were restored. Ubuntu's original `2` values were restored by the harness before the final installation.

The original 1.0.2 installer was replayed only in the disposable VM under the maintainer's explicit authorization. Its checksum was verified before execution. Its legacy firewall rules were preserved by the 1.0.3 upgrade; only the test harness later removed these known test-created rules. Administrator-owned SADP policies are also covered by regression tests to prevent UFW comment updates from being mistaken for newly owned rules.

The final VM retains 1.0.3, Git and the working source, with UFW active and SSH explicitly allowed. The unrelated test rule on port 9999 was removed. The Ubuntu base snapshot is unchanged.

## Limits and release status

- No real device IP, mask, gateway, SDK port, DHCP state or Hik-Connect binding was changed. Modification/unbind acknowledgements and errors were simulated in tests; real firmware compatibility remains unverified.
- HTTP/IPv6 configuration and enabling Hik-Connect remain disabled. Password reset remains informational.
- Only Ubuntu 24.04 amd64 was exercised. Other distributions, architectures, multiple physical adapters, routed VLAN discovery and every device firmware are not certified by these results.
- The helper still accepts device passwords as command-line arguments. That upstream transport has not been redesigned in this patch; local process visibility remains a limitation of management commands.
- VirtualBox's software graphics produced non-fatal Mesa/EGL warnings under Wayland. The GUI rendered and scanning completed.
- Older per-user source installations must use the updated source installer to retire their user launcher/desktop entry, or remove those legacy launchers manually. The Debian installer does not alter arbitrary user home directories.
- GitHub Actions runs the tests before building and publishing a tagged release. Consult the workflow run for the tagged commit to verify its result.

Local artifacts/checksums and detailed test logs are generated in `dist/`, which is ignored by Git. Published release assets are built by GitHub Actions from the tagged source commit and include their own `SHA256SUMS.txt`; archive timestamps can differ from pre-commit local builds.
