# KalOnline Auto Fuser

KalOnline Auto Fuser is a Python script designed to automate the process of "dragon fusing" in the game KalOnline. The script automates clicks, color detection, and other in-game interactions, allowing you to efficiently manage the pimping process without manual input.

## Features

- Automates the clicking process within the game.
- Detects specific colors to determine the success or failure of pimping.
- Supports multi-monitor setups.
- Allows customization of satisfaction levels and maximum reruns.
- Optional debug mode for coordinate checking and visual overlays.
- Works with the game window in the background (not minimized), so you can continue using your mouse freely.

## Requirements

- Python 3.6+
- `pywinauto`
- `Pillow`
- `colorama`
- `mss`
- `pygetwindow`

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/lt-kraken/kraken-kalonline-scripts.git
   cd KalOnlineAutoFuser
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
You can run the script using the command line. Below are some example usages:

### Prompt Usage (1st use)
   ```bash
   python KalOnlineAutoFuser.py
   ```
- Follow the command prompts for more guidance
   - Screen renames are automatically performed to include window handles

### Basic Usage
   ```bash
   python KalOnlineAutoFuser.py --handle 1051494 --satisfaction 8 --max_reruns 10
   ```
- `--handle`: Window handle ID to use for the game window.
- `--satisfaction`: Minimum satisfaction score for the fuse (1-8).
- `--max_reruns`: Maximum number of reruns.

## Debug Mode
Enable verbose output and coordinate debug overlays:

   ```bash
   python KalOnlineAutoFuser.py --handle 1051494 --satisfaction 8 --max_reruns 10 --verbose --coordinate_debug
   ```

## Available Command-Line Arguments
- `--handle`: Specify the window handle ID for the game.
- `--satisfaction`: Define the minimum satisfaction score for the fuse (1-8). The higher the number, the more desirable the fuse.
   - 1: Imoogi
   - 2: Shadow Dragon
   - 3: Sky Dragon
   - 4: Ancient Dragon
   - 5: Storm Dragon
   - 6: Violent Dragon
   - 7: Thunder Dragon
   - 8: Insanity Dragon
- `--max_reruns`: Set the maximum number of retries if the desired satisfaction score is not achieved.
- `--verbose`: Run the script in verbose mode, which provides detailed output of the operations.
- `--coordinate_debug`: Enable visual overlays to show the regions where color detection occurs.

## Important Notes
### Dependency on Color Matching
This script relies on color matching to detect the success or failure of the fuse. It is essential to keep the inventory in the lower right corner of the screen to ensure accurate color detection. Additionally, the game should be run at its default resolution of 1024p to align with the predefined coordinates used in the script.

### Black Screenshots
If you encounter black screenshots when the game window is moved to a secondary monitor, ensure that you are using the `mss` library for screen capture as it handles multi-monitor setups more robustly.

### Multi-Monitor Setup
The script supports multi-monitor setups. Ensure that your monitors are correctly configured in your operating system's display settings.

## License
This project is licensed under the GNU General Public License v3.0 - see the LICENSE file in the root for details.

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

### Contributors
- [@lt-kraken](https://www.github.com/lt-kraken)

## Acknowledgments
Thanks to the `pywinauto`, `Pillow`, `mss`, and `colorama` communities for providing the tools that make this script possible.

## Support the project!
![GitHub Sponsors](https://img.shields.io/github/sponsors/lt-kraken)
[![Patreon](https://img.shields.io/badge/Patreon-8A2BE2)](patreon.com/krakensoftware)
[![Coffee](https://img.shields.io/badge/Buy_Me_A_Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/ltkraken)

## Copyright

Copyright (C) 2024 [KrakenSoftware.eu](https://krakensoftware.eu)

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
