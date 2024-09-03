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

import argparse
import win32gui
import win32con
from pywinauto.application import Application
import pygetwindow as gw
import time
from PIL import ImageGrab, ImageDraw, Image
import numpy as np
from colorama import init, Fore, Style
import mss
import mss.tools

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pywinauto.application")


# Initialize colorama
init(autoreset=True)

class GameWindowHandler:
    def __init__(self, handle=None, max_reruns=None, min_satisfaction_score=1, verbose=False, coordinate_debug=False):
        self.window_handle = handle
        self.game_resolution = (1024, 768)        
        self.y_offset = 28  # Updated offset
        self.verbose = verbose
        self.coordinate_debug = coordinate_debug
        self.app = None
        
        self.click_positions = [(510, 443), (450, 420), (450, 420)]
        self.color_check_region = (427, 320, 589, 346)
        self.retry_delay_region = (482, 438, 541, 448)
        self.confirm_button_color = (254, 220, 187)
        self.retry_confirm_region = (426, 415, 483, 427)
        self.max_reruns = max_reruns
        self.rerun_count = 0
        self.min_satisfaction_score = min_satisfaction_score  # Default minimum satisfaction score

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

    def rename_windows(self, target_title="TheHyperNetwork"):
        def enum_window_callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd) == target_title:
                new_title = f"{target_title} ({hwnd})"
                win32gui.SetWindowText(hwnd, new_title)
                if self.verbose:
                    print(Fore.GREEN + f"Renamed window: {new_title}")

        win32gui.EnumWindows(enum_window_callback, None)

    def perform_pimping_sequence(self):
        while True:
            self.rerun_count = 0  # Reset rerun count for each session
            while self.rerun_count < self.max_reruns:
                for position in self.click_positions:
                    self.click_at_position(*position)
                    time.sleep(0.5)  # Sleep for 500 milliseconds

                time.sleep(3.5)  # Sleep for 3000 milliseconds

                detected_fuse = self.detect_fuse(self.color_check_region)
                if detected_fuse:
                    satisfaction_score = self.fuse_satisfaction[detected_fuse]
                    if satisfaction_score >= self.min_satisfaction_score:
                        print(Fore.GREEN + f"Pimping succeeded with {detected_fuse} (Satisfaction: {satisfaction_score}).")
                        return
                    else:
                        print(Fore.RED + f"Pimping failed, detected {detected_fuse} (Satisfaction: {satisfaction_score}) which is below the minimum acceptable score. Retrying... ({self.rerun_count + 1}/{self.max_reruns})")
                elif detected_fuse is None:
                    print(Fore.RED + "Pimping failed, color detection error. Stopping...")
                    return
                self.rerun_count += 1

            print(Fore.RED + "Maximum reruns reached.")
            continue_retry = input("Would you like to continue retrying for another session? (y/n): ").strip().lower()
            if continue_retry != 'y':
                print(Fore.RED + "Stopping the sequence as per user request.")
                return
            else:
                print(Fore.YELLOW + "Restarting the sequence for another session.")

    def click_at_position(self, x, y):
        # Click at the specified position using pywinauto without hijacking the mouse
        self.app.window(handle=self.window_handle).click(coords=(x, y))

        if self.verbose:
            print(Style.DIM + Fore.LIGHTBLACK_EX + f"Clicked at ({x}, {y}) within the game window.")

    def detect_fuse(self, region):
        # Get the window's rectangle
        window_rect = self.kalonline_utils.get_window_rect(self.window_handle)
        
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

        # Correctly map RGB colors to their corresponding colorama colors
        color_map = {
            (153, 153, 153): Fore.LIGHTBLACK_EX,  # Imoogi
            (0, 255, 0): Fore.GREEN,  # Shadow Dragon
            (255, 255, 0): Fore.YELLOW,  # Sky Dragon
            (0, 136, 255): Fore.CYAN,  # Ancient Dragon
            (255, 136, 68): Fore.LIGHTRED_EX,  # Storm Dragon
            (170, 85, 255): Fore.MAGENTA,  # Violent Dragon
            (255, 0, 0): Fore.RED,  # Thunder Dragon
            (255, 153, 255): Fore.LIGHTMAGENTA_EX,  # Insanity Dragon (Updated color)
        }

        for x in range(img.width):
            for y in range(img.height):
                pixel_color = img.getpixel((x, y))
                if pixel_color in self.fuse_colors:
                    fuse_name = self.fuse_colors[pixel_color]
                    color_code = color_map.get(pixel_color, Fore.WHITE)

                    print(color_code + f"Detected fuse: {fuse_name} at ({x + region[0]}, {y + region[1]})")
                    return fuse_name

        print(Fore.RED + "No matching color found in the specified region.")
        return None

    def show_debug_overlay(self, screenshot, relative_region):
        draw = ImageDraw.Draw(screenshot)
        draw.rectangle(
            [relative_region[0], relative_region[1], relative_region[2], relative_region[3]],
            outline="red",
            width=5,
        )
        screenshot.show(title=f"Debug Overlay - Region {relative_region}")

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

    def ask_for_handle(self):
        if not self.window_handle:
            handle_id = input("Please enter the window handle ID (integer): ")
            self.set_window_by_handle(handle_id)
        else:
            self.set_window_by_handle(self.window_handle)

    def ask_for_max_reruns(self):
        if not self.max_reruns:
            while True:
                try:
                    self.max_reruns = int(input("Please enter the maximum number of reruns: "))
                    break
                except ValueError:
                    print(Fore.RED + "Invalid input. Please enter a valid integer.")

    def ask_for_min_satisfaction_score(self):
        if not self.min_satisfaction_score:
            # Display the satisfaction score mapping
            print(Fore.CYAN + "Satisfaction Score Mapping:")
            for fuse_name, score in self.fuse_satisfaction.items():
                print(f"  {score}: {fuse_name}")

            # Prompt user for minimum satisfaction score
            while True:
                try:
                    self.min_satisfaction_score = int(input("\nPlease enter the minimum satisfaction score (1-8): "))
                    if 1 <= self.min_satisfaction_score <= 8:
                        break
                    else:
                        print(Fore.RED + "Invalid input. Please enter a value between 1 and 8.")
                except ValueError:
                    print(Fore.RED + "Invalid input. Please enter a valid integer.")

    def start(self):
        self.rename_windows()  # Rename the windows first
        self.ask_for_handle()
        self.ask_for_max_reruns()
        self.ask_for_min_satisfaction_score()
        self.perform_pimping_sequence()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pimping sequence automation script.")
    parser.add_argument("--handle", type=int, help="Window handle ID to use for the game window.")
    parser.add_argument("--satisfaction", type=int, help="Minimum satisfaction score for the fuse (1-8).")
    parser.add_argument("--max_reruns", type=int, help="Maximum number of reruns.")
    parser.add_argument("--verbose", action="store_true", help="Run the script in verbose mode with more detailed output.")
    parser.add_argument("--coordinate_debug", action="store_true", help="Show debug overlays for coordinate detection.")

    args = parser.parse_args()

    handler = GameWindowHandler(
        handle=args.handle,
        max_reruns=args.max_reruns,
        min_satisfaction_score=args.satisfaction,
        verbose=args.verbose,
        coordinate_debug=args.coordinate_debug
    )
    handler.start()
