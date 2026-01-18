#!/usr/bin/env python3
"""
Tapo-Pywal: Sync your Tapo smart bulb colors with pywal
"""

import asyncio
import json
import argparse
import sys
from pathlib import Path
from tapo import ApiClient

# Pywal colors path
WAL_COLORS_PATH = Path.home() / ".cache" / "wal" / "colors"
CONFIG_PATH = Path(__file__).parent / "config.json"


def load_config():
    """Load Tapo credentials from config file."""
    if not CONFIG_PATH.exists():
        print(f"Error: Config file not found at {CONFIG_PATH}")
        print("Create config.json with: email, password, device_ip")
        sys.exit(1)

    with open(CONFIG_PATH) as f:
        return json.load(f)


def parse_hex_color(hex_color: str) -> tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.strip().lstrip('#')
    return (
        int(hex_color[0:2], 16),
        int(hex_color[2:4], 16),
        int(hex_color[4:6], 16)
    )


def load_pywal_colors() -> list[tuple[int, int, int]] | None:
    """Load colors from pywal cache."""
    if not WAL_COLORS_PATH.exists():
        return None

    colors = []
    with open(WAL_COLORS_PATH) as f:
        for line in f:
            line = line.strip()
            if line and line.startswith('#'):
                try:
                    colors.append(parse_hex_color(line))
                except (ValueError, IndexError):
                    continue

    return colors if colors else None


def rgb_to_hsv(r: int, g: int, b: int) -> tuple[int, int]:
    """Convert RGB to Hue (0-360) and Saturation (0-100) for Tapo."""
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    diff = max_c - min_c

    # Hue calculation
    if diff == 0:
        h = 0
    elif max_c == r:
        h = (60 * ((g - b) / diff) + 360) % 360
    elif max_c == g:
        h = (60 * ((b - r) / diff) + 120) % 360
    else:
        h = (60 * ((r - g) / diff) + 240) % 360

    # Saturation calculation
    s = 0 if max_c == 0 else (diff / max_c) * 100

    return int(h), int(s)


async def set_color(device, r: int, g: int, b: int, brightness: int = 100):
    """Set bulb color using RGB values."""
    hue, saturation = rgb_to_hsv(r, g, b)
    print(f"Setting color: RGB({r},{g},{b}) -> HSV({hue}, {saturation})")
    await device.set_hue_saturation(hue, saturation)
    await device.set_brightness(brightness)


async def set_pywal_color(device, color_index: int = 1, brightness: int = 100):
    """Set bulb to a pywal color."""
    colors = load_pywal_colors()
    if not colors:
        print("Error: Could not load pywal colors")
        print("Make sure pywal is installed and run 'wal' first")
        return False

    if color_index >= len(colors):
        color_index = 1

    r, g, b = colors[color_index]
    print(f"Using pywal color {color_index}: RGB({r},{g},{b})")
    await set_color(device, r, g, b, brightness)
    return True


async def main():
    parser = argparse.ArgumentParser(
        description="Sync Tapo smart bulb with pywal colors",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  tapo-pywal --pywal              # Use pywal accent color (color 1)
  tapo-pywal --pywal --index 2    # Use pywal color 2
  tapo-pywal --color "#FF0000"    # Set red color
  tapo-pywal --color "255,128,0"  # Set orange color
  tapo-pywal --off                # Turn off bulb
  tapo-pywal --on                 # Turn on bulb
        """
    )

    parser.add_argument('--pywal', action='store_true',
                        help='Use pywal color')
    parser.add_argument('--index', type=int, default=1,
                        help='Pywal color index (default: 1 = accent)')
    parser.add_argument('--color', type=str,
                        help='Set color (hex: #FF0000 or RGB: 255,0,0)')
    parser.add_argument('--brightness', type=int, default=100,
                        help='Brightness 1-100 (default: 100)')
    parser.add_argument('--on', action='store_true',
                        help='Turn on bulb')
    parser.add_argument('--off', action='store_true',
                        help='Turn off bulb')
    parser.add_argument('--status', action='store_true',
                        help='Show bulb status')

    args = parser.parse_args()

    # Load config
    config = load_config()

    # Connect to device
    print(f"Connecting to Tapo L530 at {config['device_ip']}...")
    client = ApiClient(config['email'], config['password'])
    device = await client.l530(config['device_ip'])

    try:
        if args.off:
            print("Turning off...")
            await device.off()
            print("Bulb turned off.")

        elif args.on:
            print("Turning on...")
            await device.on()
            print("Bulb turned on.")

        elif args.status:
            info = await device.get_device_info()
            print(f"Device: {info.nickname}")
            print(f"Model: {info.model}")
            print(f"On: {info.device_on}")
            print(f"Brightness: {info.brightness}%")
            if hasattr(info, 'hue'):
                print(f"Hue: {info.hue}")
                print(f"Saturation: {info.saturation}")

        elif args.pywal:
            await set_pywal_color(device, args.index, args.brightness)
            print("Pywal color applied!")

        elif args.color:
            # Parse color input
            color = args.color.strip()
            if color.startswith('#'):
                r, g, b = parse_hex_color(color)
            elif ',' in color:
                parts = color.split(',')
                r, g, b = int(parts[0]), int(parts[1]), int(parts[2])
            else:
                print(f"Unknown color format: {color}")
                sys.exit(1)

            await set_color(device, r, g, b, args.brightness)
            print("Color applied!")

        else:
            parser.print_help()

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
