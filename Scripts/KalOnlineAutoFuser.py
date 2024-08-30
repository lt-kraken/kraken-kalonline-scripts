# KalOnline Auto Fuser
# Copyright (C) 2024 KrakenSoftware.eu
#
# Repository: https://github.com/lt-kraken/kraken-kalonline-scripts
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

from kalonline_utils import KalOnlineUtils
import argparse
import time
from PIL import Image
from colorama import init, Fore
import mss
import mss.tools
import warnings
import logging

# Setup basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Remove warnings from pywinauto
warnings.filterwarnings("ignore", category=UserWarning, module="pywinauto.application")

# Initialize colorama
init(autoreset=True)


class GameWindowHandler:
    def __init__(self, show_handles=False, handle=None, attempts=None, satisfaction=1, verbose=False,
                 coordinate_debug=False):
        # Globals
        self.kalonline_utils = KalOnlineUtils(handle, verbose)
        self.app = None
        self.rerun_count = 0

        self.fuse_colors = {
            (153, 153, 153): "Imoogi",
            (0, 255, 0): "Shadow Dragon",
            (255, 255, 0): "Sky Dragon",
            (0, 136, 255): "Ancient Dragon",
            (255, 136, 68): "Storm Dragon",
            (170, 85, 255): "Violent Dragon",
            (255, 0, 0): "Thunder Dragon",
            (255, 153, 255): "Insanity Dragon"  # Updated official color for Insanity Dragon
        }

        self.fuse_satisfaction = {
            "Imoogi": 1,
            "Shadow Dragon": 2,
            "Sky Dragon": 3,
            "Ancient Dragon": 4,
            "Storm Dragon": 5,
            "Violent Dragon": 6,
            "Thunder Dragon": 7,
            "Insanity Dragon": 8
        }

        # Initial
        self.show_handles = show_handles

        # Functional
        self.window_handle = handle
        self.attempts = attempts
        self.satisfaction = satisfaction

        # Debug
        self.verbose = verbose
        self.coordinate_debug = coordinate_debug

        # Settings
        self.game_resolution = (1024, 768)
        self.title_bar_offset = 28

        self.click_positions = [(510, 443), (450, 420), (450, 420)]
        self.color_check_region = (427, 320, 589, 346)
        self.retry_delay_region = (482, 438, 541, 448)
        self.confirm_button_color = (254, 220, 187)
        self.retry_confirm_region = (426, 415, 483, 427)

    def perform_pimping_sequence(self):
        try:
            logging.info("Starting Fuse sequence..")

            def should_retry():
                return input("Would you like to continue retrying for another session? (y/n): ").strip().lower() == 'y'

            while True:
                self.rerun_count = 0

                while self.rerun_count < self.attempts:
                    self.perform_click_sequence()
                    detected_fuse, satisfaction_score = self.evaluate_fuse()

                    if self.is_satisfactory_fuse(detected_fuse, satisfaction_score):
                        logging.info(f"Pimping succeeded with {detected_fuse} (Satisfaction: {satisfaction_score}).")
                        return
                    elif detected_fuse is None:
                        logging.error("Pimping failed, color detection error. Stopping...")
                        return
                    self.rerun_count += 1

                logging.warning("Maximum reruns reached.")
                if not should_retry():
                    logging.info("Stopping the sequence as per user request.")
                    return
                logging.info("Restarting the sequence for another session.")
        except Exception as e:
            logging.error(f"Error during pimping sequence: {e}")

    def perform_click_sequence(self):
        for position in self.click_positions:
            self.kalonline_utils.click_at_position(*position)
            time.sleep(0.5)
        time.sleep(3.5)

    def evaluate_fuse(self):
        detected_fuse = self.detect_fuse(self.color_check_region)
        satisfaction_score = self.fuse_satisfaction.get(detected_fuse, 0)
        return detected_fuse, satisfaction_score

    def is_satisfactory_fuse(self, detected_fuse, satisfaction_score):
        if satisfaction_score >= self.satisfaction:
            return True
        else:
            logging.warning(f"Pimping failed, detected {detected_fuse} (Satisfaction: {satisfaction_score}) which is "
                            f"below the minimum acceptable score. Retrying... ({self.rerun_count + 1}/{self.attempts})")
            return False

    def detect_fuse(self, region):
        window_rect = self.kalonline_utils.get_window_rect()

        # Calculate the region relative to the window's current position
        relative_region = {
            "left": window_rect[0] + region[0],
            "top": window_rect[1] + region[1] + self.title_bar_offset,
            "width": region[2] - region[0],
            "height": region[3] - region[1]
        }

        if self.verbose:
            logging.debug(f"Window Rect: {window_rect}")
            logging.debug(f"Relative Region: {relative_region}")

        with mss.mss() as sct:
            try:
                screenshot = sct.grab(relative_region)
                img = Image.frombytes("RGB", (screenshot.width, screenshot.height), screenshot.rgb)
            except Exception as e:
                logging.error(f"Error capturing screenshot: {e}")
                return None

        if self.coordinate_debug:
            img.show(title="Debug Overlay - Captured Region")
            img.save("debug_screenshot.png")

        for x in range(img.width):
            for y in range(img.height):
                pixel_color = img.getpixel((x, y))
                if pixel_color in self.fuse_colors:
                    fuse_name = self.fuse_colors[pixel_color]

                    logging.info(f"Detected fuse: {fuse_name} at ({x + region[0]}, {y + region[1]})")
                    return fuse_name

        logging.error("No matching color found in the specified region.")
        return None

    def ask_for_attempts(self):
        if not self.attempts:
            self.attempts = self.kalonline_utils.ask_for_input(
                prompt_message="Please enter the maximum number of attempts: ",
                validation_func=lambda x: x > 0,
                error_message="Invalid input. Please enter a valid integer."
            )

    def ask_for_min_satisfaction_score(self):
        if not self.satisfaction:
            print(Fore.CYAN + "Satisfaction Score Mapping:")
            for fuse_name, score in self.fuse_satisfaction.items():
                print(f"  {score}: {fuse_name}")

            self.satisfaction = self.kalonline_utils.ask_for_input(
                prompt_message="\nPlease enter the minimum satisfaction score (1-8): ",
                validation_func=lambda x: 1 <= x <= 8,
                error_message="Invalid input. Please enter a value between 1 and 8."
            )

    def start(self):
        if self.show_handles:
            self.kalonline_utils.rename_windows()
            return

        # Ask for input
        self.kalonline_utils.ask_for_handle()
        self.ask_for_attempts()
        self.ask_for_min_satisfaction_score()

        # Start sequence
        self.perform_pimping_sequence()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pimping sequence automation script.")

    # Initial Load
    parser.add_argument("--show_handles", action="store_true",
                        help="Add Window handle ID to the title bar of the game window.")

    # Functional workings
    parser.add_argument("--handle", type=int, help="Window handle ID to use for the game window.")
    parser.add_argument("--satisfaction", type=int, help="Minimum satisfaction score for the fuse (1-8).")
    parser.add_argument("--attempts", type=int, help="Maximum number of attempts.")

    # Debug
    parser.add_argument("--verbose", action="store_true",
                        help="Run the script in verbose mode with more detailed output.")
    parser.add_argument("--coordinate_debug", action="store_true", help="Show debug overlays for coordinate detection.")

    args = parser.parse_args()

    handler = GameWindowHandler(
        show_handles=args.show_handles,
        handle=args.handle,
        attempts=args.attempts,
        satisfaction=args.satisfaction,
        verbose=args.verbose,
        coordinate_debug=args.coordinate_debug
    )
    handler.start()
