# Installation

## Requirements

- Python 3.10+
- Linux (tested), other platforms may work via pyserial

## Install from GitHub

```bash
# Using uv (recommended)
uv add git+https://github.com/osoekawaitlab/ch9329py.git

# Using pip
pip install git+https://github.com/osoekawaitlab/ch9329py.git
```

## Linux Setup

### 1. Find Serial Port

```bash
# USB-to-Serial adapter
ls /dev/ttyUSB*  # Usually /dev/ttyUSB0

# Hardware UART
ls /dev/ttyS*    # /dev/ttyS0, /dev/serial0, etc.
```

### 2. Grant Permissions

```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Log out and back in for changes to take effect
```

### 3. Verify

```python
import ch9329py
print(ch9329py.__version__)  # Should print: 0.2.0
```

## Development Setup

```bash
git clone https://github.com/osoekawaitlab/ch9329py.git
cd ch9329py

# Install dependencies
uv sync

# Run tests
uv run nox -s tests
```

## Troubleshooting

### Permission Denied

```bash
sudo usermod -a -G dialout $USER
# Then log out and back in
```

### Device Not Found

```bash
# Check dmesg for device detection
dmesg | grep tty

# Verify device connection
ls -l /dev/ttyUSB0
```

### Import Error

```bash
# Verify installation
pip list | grep ch9329py

# Reinstall if needed
pip uninstall ch9329py
pip install git+https://github.com/osoekawaitlab/ch9329py.git
```

## Platform Notes

**Linux**: Fully tested and supported.

**Windows/macOS**: Not tested. May work since pyserial supports these platforms (use `COM3` on Windows, `/dev/tty.usbserial-*` on macOS). Contributions welcome!

**Docker**: Grant device access with `--device=/dev/ttyUSB0`

**WSL**: Limited serial support. Consider native Linux or Windows.
