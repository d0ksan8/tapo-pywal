# Tapo-Pywal

Sync your TP-Link Tapo smart bulb colors with [pywal](https://github.com/dylanaraps/pywal) color schemes.

Change your wallpaper, and watch your room lighting match automatically.

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## Features

- Sync Tapo L530/L630 bulb colors with pywal palette
- Set custom RGB or hex colors
- Control brightness
- Simple CLI interface
- Easy integration with shell aliases

## Supported Devices

- Tapo L530 (tested)
- Tapo L630
- Other Tapo color bulbs (should work)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/d0ksan8/tapo-pywal.git
   cd tapo-pywal
   ```

2. **Create virtual environment and install dependencies:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install tapo
   ```

3. **Create config file:**
   ```bash
   cp config.example.json config.json
   ```

4. **Edit config.json with your Tapo credentials:**
   ```json
   {
       "email": "your-tapo-email@example.com",
       "password": "your-tapo-password",
       "device_ip": "192.168.1.xxx"
   }
   ```

   > Find your bulb's IP in the Tapo app: Device Settings → Device Info

## Usage

```bash
# Activate virtual environment
source .venv/bin/activate

# Apply pywal accent color
python3 tapo_pywal.py --pywal

# Use specific pywal color (0-15)
python3 tapo_pywal.py --pywal --index 2

# Set custom color
python3 tapo_pywal.py --color "#FF6600"
python3 tapo_pywal.py --color "255,100,50"

# Adjust brightness (1-100)
python3 tapo_pywal.py --pywal --brightness 50

# Turn on/off
python3 tapo_pywal.py --on
python3 tapo_pywal.py --off

# Check status
python3 tapo_pywal.py --status
```

## Auto-sync with Pywal

Add this to your `~/.bashrc` or `~/.zshrc`:

```bash
wal() {
    /usr/bin/wal "$@"
    /path/to/tapo-pywal/.venv/bin/python3 /path/to/tapo-pywal/tapo_pywal.py --pywal --brightness 80 >/dev/null 2>&1 &
}
```

Now every time you run `wal -i wallpaper.jpg`, your bulb will automatically match!

## Combine with Keyboard RGB

Using [aula-f87pro](https://github.com/Ahorts/aula-f87pro) for keyboard RGB? Combine them:

```bash
wal() {
    /usr/bin/wal "$@"
    # Keyboard
    pkill -f "aula-f87pro" 2>/dev/null
    nohup /path/to/aula-f87pro/.venv/bin/aula-f87pro --pywal --duration 0 >/dev/null 2>&1 &
    disown
    # Tapo bulb
    /path/to/tapo-pywal/.venv/bin/python3 /path/to/tapo-pywal/tapo_pywal.py --pywal --brightness 80 >/dev/null 2>&1 &
}
```

## How It Works

1. Reads colors from `~/.cache/wal/colors` (pywal output)
2. Converts RGB to HSV (Tapo uses hue/saturation)
3. Sends color command via Tapo API

## Requirements

- Python 3.9+
- [pywal](https://github.com/dylanaraps/pywal)
- TP-Link Tapo account
- Tapo color bulb on local network

## License

MIT License

## Credits

- [tapo](https://github.com/mihai-dinculescu/tapo) - Unofficial Tapo API client
- [pywal](https://github.com/dylanaraps/pywal) - Color scheme generator

## Disclaimer

This project is not affiliated with TP-Link or Tapo. Use at your own risk.
