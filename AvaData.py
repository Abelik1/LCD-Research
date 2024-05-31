import time
# from avaspec import *
import psutil
import subprocess
import pyautogui
import pygetwindow as gw

class AppControl():
    ### Window Control ### 
    def is_application_open(self, name):
        """Check if there is any running process that contains the given name."""
        for proc in psutil.process_iter(['name']):
            try:
                if name.lower() in proc.info['name'].lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return False

    def focus_application_window(self, window_title):
        """Focus and maximize the window with the given title."""
        windows = gw.getWindowsWithTitle(window_title)
        if not windows:
            print(f"No windows found with title containing: {window_title}")
            return False
        for win in windows:
            try:
                print(f"Attempting to activate window: {win.title}")
                win.activate()
                win.maximize()
                return True
            except Exception as e:
                print("Error bringing the window to front:", e)
        return False

    def open_application(self, path, Avantes_exe, window_title):
        """Opens an application if it's not already running and focuses the window."""
        if not self.is_application_open(Avantes_exe):
            subprocess.Popen(path)
            time.sleep(5)  # Wait for the application to open
        self.focus_application_window(window_title)

    def type_in_application(self, text):
        """Types a string of text into the open application."""
        pyautogui.typewrite(text, interval=0.1)     
    ### Oscilloscope Control ###
    
