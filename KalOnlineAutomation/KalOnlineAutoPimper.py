# KalOnline Auto Pimper
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
import time
import mss
import mss.tools
from PIL import Image
import argparse
import warnings
from colorama import init, Fore
from pynput import mouse, keyboard
from pynput.keyboard import Key
from pywinauto import timings
import logging

# Setup basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Reduce the default timings to speed up script execution
timings.Timings.after_clickinput_wait = 0.1   # Time to wait after a click input
timings.Timings.after_menu_wait = 0.1         # Time to wait after opening/closing a menu
timings.Timings.after_sendkeys_key_wait = 0.1 # Time between keystrokes when using send_keys

timings.Timings.drag_n_drop_move_mouse_wait = 0.001
timings.Timings.before_drag_wait = 0
timings.Timings.before_drop_wait = 0
timings.Timings.after_drag_n_drop_wait = 0

warnings.filterwarnings("ignore", category=UserWarning, module="pywinauto.application")

# Initialize colorama
init(autoreset=True)


class GameAutomationHandler:
    def __init__(self, show_handles=False, handle=None, repair_only=False, auto_sell_type=None, repair_enabled=True,
                 check_kings=False, attempts_before_repair=1, runs=None, verbose=False, coordinate_debug=False):
        # Globals
        self.kalonline_utils = KalOnlineUtils(handle, verbose)
        self.app = None

        # Initial
        self.show_handles = show_handles

        # Functional
        self.window_handle = handle
        self.repair_only = repair_only
        self.auto_sell_type = auto_sell_type
        self.repair_enabled = repair_enabled
        self.check_kings = check_kings
        self.attempts_before_repair = attempts_before_repair
        self.runs = runs

        # Debug
        self.verbose = verbose
        self.coordinate_debug = coordinate_debug

        # Settings
        self.game_resolution = (1024, 768)
        self.title_bar_offset = 28

        self.coordinates = {}
        self.last_position = None

        if self.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

    def capture_coordinates(self, prompt_message):
        print(prompt_message + " Press F6 to capture.")
        with mouse.Listener(
            on_click=lambda x, y, button, pressed: False) as listener:
            listener.join()

        with keyboard.Listener(
            on_press=self.on_press) as listener:
            listener.join()

        return self.kalonline_utils.to_relative(self.last_position)

    def on_press(self, key):
        if key == Key.f6:
            self.last_position = mouse.Controller().position
            return False  # Stop listener

    def drag_item(self, start_pos, end_pos, count=1):
        for _ in range(count):
            self.kalonline_utils.app.window(handle=self.window_handle).drag_mouse(
                press_coords=start_pos,
                release_coords=end_pos,
                button="left"
            )
            self.kalonline_utils.click_at_position((446, 430))

    def check_color_presence(self, region):
        window_rect = self.kalonline_utils.get_window_rect()

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

        success_color_range = [((16, 58, 126), (36, 78, 146)), ((16, 113, 215), (36, 133, 235))]
        failure_color_range = [((148, 0, 0), (188, 20, 20))]

        for x in range(screenshot.width):
            for y in range(screenshot.height):
                current_color = img.getpixel((x, y))
                if any(self.color_in_range(current_color, range) for range in success_color_range):
                    logging.debug(f'success range - color {current_color} identified')
                    return "success"
                if any(self.color_in_range(current_color, range) for range in failure_color_range):
                    logging.debug(f'failure range - color {current_color} identified')
                    return "failure"

        return None

    @staticmethod
    def color_in_range(color, color_range):
        """
        Check if a color is within the provided range of target colors.

        Parameters:
        - color: The current color as a tuple (r, g, b).
        - color_range: A tuple of two tuples, defining the minimum and maximum of the color range ((min_r, min_g, min_b), (max_r, max_g, max_b)).

        Returns:
        - True if the color is within the range, False otherwise.
        """
        (r, g, b) = color
        (min_r, min_g, min_b), (max_r, max_g, max_b) = color_range
        return min_r <= r <= max_r and min_g <= g <= max_g and min_b <= b <= max_b

    def perform_drag_sequence(self):
        try:
            logging.info("Starting pimping sequence..")

            if self.repair_only:
                self.perform_repair_only()
                return

            for run in range(self.runs):
                self.handle_run(run)
                if self.auto_sell_type == 0:
                    break

        except Exception as e:
            logging.error(f"Error during pimping sequence: {e}")

    def perform_repair_only(self):
        logging.warning("Only repairing the weapon...")
        self.drag_item((760, 487), (832, 487), self.runs)

    def handle_run(self, run):
        attempts = 0
        success = False
        second_attempt = False

        while not success:
            attempts = self.handle_attempts_and_repair(attempts)
            self.drag_item(self.coordinates['talisman_item'], self.coordinates['weapon_item'])
            time.sleep(6)

            result = self.check_color_presence((360, 210, 705, 265))
            success, second_attempt = self.handle_pimping_result(result, second_attempt)

            if not success:
                attempts += 1

            if success:
                self.perform_auto_sell()

        logging.info(f"Run {run + 1}/{self.runs} complete.")

    def handle_attempts_and_repair(self, attempts):
        if attempts >= self.attempts_before_repair:
            if self.repair_enabled:
                logging.info(f"Repairing the weapon (x{attempts*5}) after {attempts} attempts...")
                self.drag_item(self.coordinates['repair_item'], self.coordinates['weapon_item'], attempts * 5)
            if self.auto_sell_type == 2:
                logging.info("Maximum pimp attempts for item reached, selling to store unpimped.")
                self.perform_auto_sell()
            return 0  # Reset attempts after repair
        return attempts

    def handle_pimping_result(self, result, second_attempt):
        if result == "success":
            logging.info("Pimping succeeded.")
            return self.handle_kings_upgrade(second_attempt)
        else:
            logging.warning("Pimping failed.")
            return False, second_attempt

    def handle_kings_upgrade(self, second_attempt):
        if self.check_kings and not second_attempt:
            response = input(Fore.YELLOW + f"Did this result in a 'Kings' upgrade? (yes/no): ").strip().lower()
            if response in ('yes', 'y'):
                return True, second_attempt  # Success, no need to change second_attempt
            else:
                logging.warning("Continuing to attempt pimping...")
                return False, True  # Not successful, update second_attempt to True
        elif self.check_kings and second_attempt:
            logging.info("Confirmed 'Kings' upgrade on second success.")
        return True, second_attempt  # Success, no further changes needed

    def perform_auto_sell(self):
        if self.auto_sell_type == 0:
            return

        if self.auto_sell_type == 1 or self.auto_sell_type == 2:
            logging.info("Selling item to merchant...")
            self.kalonline_utils.right_click_at_position(self.coordinates['weapon_item'])
            self.kalonline_utils.click_at_position((466, 417))

    def ask_for_runs(self):
        if not self.runs:
            self.runs = self.kalonline_utils.ask_for_input(
                prompt_message="Please enter the maximum number of runs: ",
                validation_func=lambda x: x > 0,
                error_message="Invalid input. Please enter a valid integer."
            )

    def ask_for_attempts_before_repair(self):
        if not self.attempts_before_repair:
            self.attempts_before_repair = self.kalonline_utils.ask_for_input(
                prompt_message="Please enter the number of pimp attempts before we should repair (warning: each "
                               "failed attempt decreased durability by 5, make sure your weapon is repaired "
                               "beforehand and attempts do not exceed item maximum-5 durability: ",
                validation_func=lambda x: 1 <= x <= 6,
                error_message="Invalid input. Please enter a value between 1 and 6."
            )

    def ask_for_auto_sell_type(self):
        if not self.auto_sell_type:
            self.auto_sell_type = self.kalonline_utils.ask_for_input(
                prompt_message="Please enter the desired sell type (0 = off, 1 = when successful, 2 = when successful "
                               "or after failed attempts: ",
                validation_func=lambda x: 0 <= x <= 2,
                error_message="Invalid input. Please enter a value between 0 and 2."
            )

    def ask_for_coordinates(self):
        self.ask_for_repair_item_coordinate()
        self.ask_for_talisman_coordinate()
        self.ask_for_item_coordinate()
        logging.info(f"coordinates recorded successfully")
        logging.info(f"starting in 3 seconds..")
        time.sleep(1)
        logging.info(f"starting in 2 seconds..")
        time.sleep(1)
        logging.info(f"starting in 1 second...")
        time.sleep(1)

    def ask_for_repair_item_coordinate(self):
        if self.repair_only or self.repair_enabled:
            self.coordinates['repair_item'] = self.capture_coordinates(Fore.YELLOW + f"Hover over the repair item")
            logging.info(f"repair_item coordinates set to {self.coordinates['repair_item']}")

    def ask_for_talisman_coordinate(self):
        if not self.repair_only:
            self.coordinates['talisman_item'] = self.capture_coordinates(Fore.YELLOW + f"Hover over the talisman item")
            logging.info(f"talisman_item coordinates set to {self.coordinates['talisman_item']}")

    def ask_for_item_coordinate(self):
        self.coordinates['weapon_item'] = self.capture_coordinates(Fore.YELLOW + f"Hover over the weapon/armor item")
        logging.info(f"weapon_item coordinates set to {self.coordinates['weapon_item']}")

    def start(self):
        if self.show_handles:
            self.kalonline_utils.rename_windows()
            return

        # Ask for input
        self.kalonline_utils.ask_for_handle()
        self.ask_for_runs()
        self.ask_for_attempts_before_repair()
        self.ask_for_auto_sell_type()
        self.ask_for_coordinates()

        self.perform_drag_sequence()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pimping sequence automation script.")

    # Initial Load
    parser.add_argument("--show_handles", action="store_true",
                        help="Add Window handle ID to the title bar of the game window.")

    # Functional workings
    parser.add_argument("--handle", type=int, help="Window handle ID to use for the game window.")
    parser.add_argument("--runs", type=int, help="Number of runs to perform.")
    parser.add_argument("--attempts_before_repair", type=int, help="Number of runs to perform.")
    parser.add_argument("--repair", action="store_true", help="Enable repair functionality.")
    parser.add_argument("--repair-only", action="store_true", help="Only perform repair actions.")
    parser.add_argument("--auto_sell_type", type=int, choices=[0, 1, 2], help="Auto-sell type.")
    parser.add_argument("--kings", action="store_true", help="Check for 'Kings' upgrade and confirm before stopping.")

    # Debug
    parser.add_argument("--verbose", action="store_true",
                        help="Run the script in verbose mode with more detailed output.")
    parser.add_argument("--coordinate_debug", action="store_true", help="Show debug overlays for coordinate detection.")

    args = parser.parse_args()

    if args.repair_only and args.auto_sell_type is not None:
        raise ValueError("Cannot set both --repair-only and --auto-sell-type options at the same time.")

    if args.repair_only and args.kings:
        raise ValueError("Cannot set both --repair-only and --kings options at the same time.")

    handler = GameAutomationHandler(
        show_handles=args.show_handles,

        handle=args.handle,
        repair_only=args.repair_only,
        repair_enabled=args.repair,
        auto_sell_type=args.auto_sell_type,
        check_kings=args.kings,
        attempts_before_repair=args.attempts_before_repair,
        runs=args.runs,

        verbose=args.verbose,
        coordinate_debug=args.coordinate_debug
    )
    handler.start()

