import win32gui
from pywinauto.application import Application
from PIL import ImageDraw
import os
import pygame
import logging

# Setup basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialization
pygame.mixer.init()
pygame.mixer.music.load('ding.mp3')

# Disable welcome message from PyGame
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"


class KalOnlineUtils:
    def __init__(self, handle=None, verbose=False):
        self.window_handle = handle
        self.verbose = verbose
        self.app = None

        if self.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

    def rename_windows(self, target_title="TheHyperNetwork"):
        try:
            def enum_window_callback(hwnd, _):
                if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd) == target_title:
                    new_title = f"{target_title} ({hwnd})"
                    win32gui.SetWindowText(hwnd, new_title)
                    if self.verbose:
                        logging.debug(f"Renamed window: {new_title}")

            win32gui.EnumWindows(enum_window_callback, None)
        except Exception as e:
            logging.error(f"Failed to rename windows: {e}")

    def click_at_position(self, x, y):
        try:
            if not self.app:
                raise ValueError("Application is not connected. Cannot click.")

            self.app.window(handle=self.window_handle).click(coords=(x, y))
            if self.verbose:
                logging.debug(f"Clicked at ({x}, {y}) within the game window.")
        except Exception as e:
            logging.error(f"Failed to click at position ({x}, {y}): {e}")

    @staticmethod
    def show_debug_overlay(screenshot, relative_region):
        draw = ImageDraw.Draw(screenshot)
        draw.rectangle(
            (relative_region[0], relative_region[1], relative_region[2], relative_region[3]),
            outline="red",
            width=5,
        )
        screenshot.show(title=f"Debug Overlay - Region {relative_region}")

    def set_window_by_handle(self, handle_id):
        try:
            self.window_handle = int(handle_id)
            window_title = win32gui.GetWindowText(self.window_handle)
            if not window_title:
                raise ValueError("The provided handle does not correspond to a valid window.")
            logging.info(f"Valid window handle: {self.window_handle} - Window Title: {window_title}")
            self.app = Application().connect(handle=self.window_handle)
        except ValueError as ve:
            logging.error(f"Invalid handle ID. Please enter a valid integer: {ve}")
        except Exception as e:
            logging.error(f"Failed to set window by handle: {e}")

    def get_window_rect(self):
        return win32gui.GetWindowRect(self.window_handle)

    def ask_for_handle(self):
        if not self.window_handle:
            self.window_handle = self.ask_for_input(
                prompt_message="Please enter the window handle ID (integer): ",
                validation_func=lambda x: x > 0,
                error_message="Invalid handle ID. Please enter a valid integer."
            )
        self.set_window_by_handle(self.window_handle)

    @staticmethod
    def ask_for_input(prompt_message, validation_func=None,
                      error_message="Invalid input. Please try again."):
        while True:
            try:
                user_input = int(input(prompt_message))
                if validation_func and not validation_func(user_input):
                    logging.error(error_message)
                    continue
                return user_input
            except ValueError:
                logging.error(error_message)

    @staticmethod
    def play_sound():
        try:
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                continue
        except pygame.error as e:
            logging.error(f"Failed to play sound: {e}")
        finally:
            pygame.mixer.quit()  # Ensure pygame is properly quit even if an error occurs
