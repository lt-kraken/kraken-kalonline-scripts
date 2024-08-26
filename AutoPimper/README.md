# KalOnline Auto Pimper

KalOnline Auto Pimper is a Python script designed to automate the process of "pimping" in the game KalOnline. The script automates clicks, color detection, and other in-game interactions, allowing you to efficiently manage the pimping process without manual input.

## Features

- **Automated Pimping**: Automatically pimps items based on set criteria.
- **Dynamic Coordinate Capture**: Captures coordinates for actions based on user input to adapt to different game layouts.
- **Repair Functionality**: Automatically repairs items if pimping fails a set number of times.
- **Kings Upgrade Check**: Optionally checks for 'Kings' upgrades and confirms before proceeding.

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
   cd KalOnlineAutoPimper
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
You can run the script using the command line. Below are some example usages:

### Prompt Usage (1st use)
   ```bash
   python KalOnlineAutoPimper.py
   ```
- Follow the command prompts for more guidance
   - Screen renames are automatically performed to include window handles

### Basic Usage
   ```bash
   python KalOnlineAutoPimper.py --handle <window_handle> [--runs <number_of_runs>] [--repair] [--repair-only] [--auto-sell-type <0, 1, 2>] [--kings]
   ```
- `--handle`: Window handle ID to use for the game window.
- `--runs`: Number of runs to perform (default is 1).
- `--repair`: Enable repair functionality.
- `--repair`-only: Only perform repair actions, no pimping.
- `--auto`-sell-type: Defines the auto-sell behavior; 0 = do not sell, 1 = sell after success, 2 = sell if failed after all retries.
- `--kings`: Check for 'Kings' upgrade and confirm before stopping.

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
