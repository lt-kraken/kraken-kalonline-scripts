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

import time
import win32con
import win32gui
import mss
import mss.tools
from PIL import ImageGrab, ImageDraw, Image
import argparse
import warnings
from colorama import init, Fore, Style
from pywinauto.application import Application
from pynput import mouse, keyboard
from pynput.keyboard import Key, Listener
from pywinauto import timings

# Reduce the default timings to speed up script execution
timings.Timings.after_clickinput_wait = 0.1  # Time to wait after a click input
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
    def __init__(self, handle=None, repair_only=False, auto_sell_type=0, repair_enabled=True, check_kings=False, attempts_before_repair=1, runs=1):
        self.window_handle = handle
        self.game_resolution = (1024, 768)        
        self.y_offset = 28  # Updated offset
        self.verbose = False
        self.coordinate_debug = False
        self.app = None
        
        self.repair_only = repair_only
        self.auto_sell_type = auto_sell_type
        self.repair_enabled = repair_enabled
        self.check_kings = check_kings
        self.attempts_before_repair = attempts_before_repair
        self.runs = runs
        self.coordinates = {}

    def rename_windows(self, target_title="TheHyperNetwork"):
        def enum_window_callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd) == target_title:
                new_title = f"{target_title} ({hwnd})"
                win32gui.SetWindowText(hwnd, new_title)
                if self.verbose:
                    print(Fore.GREEN + f"Renamed window: {new_title}")

        win32gui.EnumWindows(enum_window_callback, None)

    def set_window_by_handle(self, handle_id):
        try:            
            self.window_handle = int(handle_id)
            window_title = win32gui.GetWindowText(self.window_handle)
            if window_title:
                print(f"Valid window handle: {self.window_handle} - Window Title: {window_title}")
                self.app = Application().connect(handle=self.window_handle)
            else:
                print(Fore.RED + "The provided handle does not correspond to a valid window.")
        except ValueError:
            print(Fore.RED + "Invalid handle ID. Please enter a valid integer.")

    def to_relative(self, absolute_coords):
        """ Convert absolute screen coordinates to coordinates relative to the window. """
        window_rect = self.get_window_rect(self.window_handle)
        return (absolute_coords[0] - window_rect[0], absolute_coords[1] - window_rect[1])

    def capture_coordinates(self, prompt_message):
        print(prompt_message + " Press F6 to capture.")
        with mouse.Listener(
            on_click=lambda x, y, button, pressed: False) as listener:
            listener.join()

        with keyboard.Listener(
            on_press=self.on_press) as listener:
            listener.join()

        return self.to_relative(self.last_position)

    def on_press(self, key):
        if key == Key.f6:
            self.last_position = mouse.Controller().position
            return False  # Stop listener

    def drag_item(self, start_pos, end_pos, count=1):
        for _ in range(count):
            self.app.window(handle=self.window_handle).drag_mouse(
                press_coords=start_pos, 
                release_coords=end_pos, 
                button="left"
            )
            time.sleep(0.01)
            self.click_at_position((446, 430))  # Ensure this is also adjusted if necessary
            
    def ask_for_handle(self):
        if not self.window_handle:
            handle_id = input("Please enter the window handle ID (integer): ")
            self.set_window_by_handle(handle_id)
        else:
            self.set_window_by_handle(self.window_handle)

    def click_at_position(self, coords):
        # Click at the specified position using pywinauto without hijacking the mouse
        self.app.window(handle=self.window_handle).click(coords=coords)

        #if self.verbose:
        #    print(Style.DIM + Fore.LIGHTBLACK_EX + f"Clicked at ({x}, {y}) within the game window.")
    
    def right_click_at_position(self, coords):
        # Click at the specified position using pywinauto without hijacking the mouse       
        self.app.window(handle=self.window_handle).right_click(coords=coords)

        #if self.verbose:
        #    print(Style.DIM + Fore.LIGHTBLACK_EX + f"Clicked at ({x}, {y}) within the game window.")

    def get_window_rect(self, hwnd):
        return win32gui.GetWindowRect(hwnd)

    def check_color_presence(self, region):
        # Get the window's rectangle
        window_rect = self.get_window_rect(self.window_handle)
        
        # Calculate the region relative to the window's current position
        relative_region = {
            "left": window_rect[0] + region[0],
            "top": window_rect[1] + region[1] + self.y_offset,
            "width": region[2] - region[0],
            "height": region[3] - region[1]
        }

        # Debugging: Print out the calculated regions
        if self.verbose:
            print(f"Window Rect: {window_rect}")
            print(f"Relative Region: {relative_region}")
            
        with mss.mss() as sct:
            try:
                screenshot = sct.grab(relative_region)
                img = Image.frombytes("RGB", (screenshot.width, screenshot.height), screenshot.rgb)
            except Exception as e:
                print(Fore.RED + f"Error capturing screenshot: {e}")
                return None
        
        # Optionally show an overlay of the region being checked
        if self.coordinate_debug:
            img.show(title="Debug Overlay - Captured Region")

        # Save the screenshot for debug purposes
        img.save("debug_screenshot.png")
        
        success_color_range = [((16, 58, 126), (36, 78, 146)), ((16, 113, 215), (36, 133, 235))]
        failure_color_range = [((148, 0, 0), (188, 20, 20))]
        
        for x in range(screenshot.width):
            for y in range(screenshot.height):
                current_color = img.getpixel((x, y))
                if any(self.color_in_range(current_color, range) for range in success_color_range):
                    return "success"
                if any(self.color_in_range(current_color, range) for range in failure_color_range):
                    return "failure"
                      
        return None

    def color_in_range(self, color, color_range):
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
        if self.repair_only:
            print(Fore.CYAN + f"Only repairing the weapon...")
            self.drag_item((760, 487), (832, 487), self.runs)
            return


        for run in range(self.runs):
            attempts = 0
            success = False
            second_attempt = False

            while not success:
                if attempts == self.attempts_before_repair:
                    if self.repair_enabled:
                        print(Fore.CYAN + f"Repairing the weapon {attempts * 5} times...")
                        self.drag_item(self.coordinates['repair_item'], self.coordinates['weapon_item'], attempts * 5)
                    attempts = 0

                self.drag_item(self.coordinates['talisman_item'], self.coordinates['weapon_item'])
                time.sleep(6)

                result = self.check_color_presence((360, 210, 705, 265))
                if result == "success":
                    print(Fore.GREEN + f"Pimping succeeded.")
                    if self.check_kings and not second_attempt:
                        response = input(Fore.YELLOW + f"Did this result in a 'Kings' upgrade?\033 (\033[4my\033[0mes/\033[4mn\033[0mo): ")
                        if response.lower() == 'yes' or response.lower() == 'y':
                            success = True
                        else:
                            print(Fore.LIGHTBLACK_EX + f"Continuing to attempt pimping...")
                            second_attempt = True
                            continue
                    elif self.check_kings and second_attempt:
                        print(Fore.GREEN + f"Confirmed 'Kings' upgrade on second success.")
                        success = True
                    else:
                        success = True

                    if self.auto_sell_type == 1:
                        print(Fore.CYAN + f"Selling item to merchant...")
                        self.right_click_at_position(self.coordinates['weapon_item'])
                        self.click_at_position((466, 417))
                else:
                    print(Fore.RED + f"Pimping failed {attempts + 1}/{self.attempts_before_repair}")
                    attempts += 1

            print(Fore.LIGHTBLACK_EX + f"Run {run + 1}/{self.runs} complete.")

    def start(self):
        self.rename_windows("TheHyperNetwork")
        self.ask_for_handle()
        if not self.repair_only:
            self.coordinates['repair_item'] = self.capture_coordinates(Fore.YELLOW + f"Hover over the repair item")
            print(Fore.LIGHTBLACK_EX + f"repair_item coordinates set to {self.coordinates['repair_item']}")
            self.coordinates['talisman_item'] = self.capture_coordinates(Fore.YELLOW + f"Hover over the talisman item")
            print(Fore.LIGHTBLACK_EX + f"talisman_item coordinates set to {self.coordinates['talisman_item']}")
            self.coordinates['weapon_item'] = self.capture_coordinates(Fore.YELLOW + f"Hover over the weapon/armor item")
            print(Fore.LIGHTBLACK_EX + f"weapon_item coordinates set to {self.coordinates['weapon_item']}")
            print(Fore.GREEN + f"coordinates recorded succesfully")
            print(Fore.LIGHTBLACK_EX + f"starting in 3 seconds..")
            time.sleep(1)
            print(Fore.LIGHTBLACK_EX + f"starting in 2 seconds..")
            time.sleep(1)
            print(Fore.LIGHTBLACK_EX + f"starting in 1 second..")
            time.sleep(1)
            
        print("Starting pimping sequence..")
        self.perform_drag_sequence()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Game Automation Script for Pimping.")
    parser.add_argument("--handle", type=int, required=True, help="Window handle ID to use for the game window.")
    parser.add_argument("--runs", type=int, default=1, help="Number of runs to perform.")
    parser.add_argument("--attempts-before-repair", type=int, default=5, help="Number of runs to perform.")
    parser.add_argument("--repair", action="store_true", help="Enable repair functionality.")
    parser.add_argument("--repair-only", action="store_true", help="Only perform repair actions.")
    parser.add_argument("--auto-sell-type", type=int, choices=[0, 1, 2], help="Auto-sell type.")
    parser.add_argument("--kings", action="store_true", help="Check for 'Kings' upgrade and confirm before stopping.")
    args = parser.parse_args()

    if args.repair_only and args.auto_sell_type is not None:
        raise ValueError("Cannot set both --repair-only and --auto-sell options at the same time.")

    game_handler = GameAutomationHandler(args.handle, args.repair_only, args.auto_sell_type, args.repair, args.kings, args.attempts_before_repair, args.runs)
    
    game_handler.start()

