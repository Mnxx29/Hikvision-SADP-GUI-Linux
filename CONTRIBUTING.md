# Contributing

Report your OS/version, desktop session (X11/Wayland), adapter and VLAN setup, device model/firmware, and the relevant output of `bash diagnostico.sh`. Remove passwords and unnecessary device identifiers from reports.

## Development (Ubuntu 24.04)

```bash
sudo apt install python3 python3-pyqt6 qt6-wayland git
python3 gui_sadp.py
QT_QPA_PLATFORM=offscreen python3 -m unittest discover -s tests -v
```

For a virtual environment, install [requirements.txt](requirements.txt) with pip. Python 3.9+ is the declared minimum. CI runs the complete suite on Ubuntu 24.04's Python/PyQt6; core tests can run without Qt, in which case desktop tests are explicitly skipped.

Wrap UI strings with `t()` and update both dictionaries in [i18n.py](i18n.py). Keep English as the fallback. Parser/validation changes need regression cases for rejected and unknown responses, not just successful examples. Never test network modification or unbind against production devices.

## Packaging

Install `golang-go` (Go 1.21+ bootstrap) and `dpkg-dev`, then:

```bash
bash packaging/build-deb.sh
```

The version comes from [VERSION](VERSION). Packages and checksums go to `dist/`. The build always fetches the exact helper commit and toolchain in [packaging/upstream.env](packaging/upstream.env); an old executable in the repository is not reused. Review upstream changes before updating that file. `SOURCE_DATE_EPOCH` controls package archive timestamps.

Before release, run the full tests, check shell syntax, test a clean install, upgrade from the previous release, and remove/purge in a disposable VM. Validate that owned network settings are restored while existing/admin-modified settings are kept. Test any active firewall with an SSH allowance in place. Keep hardware validation separate from simulated responses and record limitations in `docs/validation-VERSION.md`.

Update `VERSION`, `CHANGELOG.md`, README install examples and release notes together. The tag must match `VERSION`; the release workflow runs tests before building and publishing. Do not tag or publish until the maintainer approves the prepared artifacts.

License: [MIT](LICENSE).
