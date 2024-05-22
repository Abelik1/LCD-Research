# % = integer
# Single precision floating = As single
import pyautogui
import subprocess
import time
import numpy as np
import sys
import inspect
import ctypes
import struct
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QHBoxLayout,QMessageBox

import globals
from PyQt5.QtCore import *


if 'linux' in sys.platform: # Linux will have 'linux' or 'linux2'
    lib = ctypes.CDLL("/usr/local/lib/libavs.so.0")
    func = ctypes.CFUNCTYPE
elif 'darwin' in sys.platform: # macOS will have 'darwin'
    lib = ctypes.CDLL("/usr/local/lib/libavs.0.dylib")
    func = ctypes.CFUNCTYPE
else: # Windows will have 'win32' or 'cygwin'
    import ctypes.wintypes
    if (ctypes.sizeof(ctypes.c_voidp) == 8): # 64 bit
        WM_MEAS_READY = 0x8001
        lib = ctypes.WinDLL("./avaspecx64.dll")
        func = ctypes.WINFUNCTYPE
    else:
        WM_MEAS_READY = 0x0401
        lib = ctypes.WinDLL("./avaspec.dll")
        func = ctypes.WINFUNCTYPE

Gen_id = 0
dev_Osc, Command, param, Out_File, Out_Data, Volt_List, Temp_List, ReadBuffer = "", "", "", "", "", "", "", ""
SSComment = ""
Frequency = [0.0] * 300
Voltage = [0.0] * 300
Temperature = [0.0] * 5000
Freq, Amplitude, Offset, AmpGain, AvPer, VScal, VScalMax, Vmax = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
Temp_Wait, LastTemp, WaitV, WaitingVoltage, Accuracy, CurrentT, SetT = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
Num_Volt, Num_Temp, TemRes = 0, 0, 0
Fast, AST, ASV, Expire, DCmode = False, False, False, False, False
EndOfProgram = None
da = None

def AVS_Init(a_Port = 0):
    prototype = func(ctypes.c_int, ctypes.c_int)
    paramflags = (1, "port",),
    AVS_Init = prototype(("AVS_Init", lib), paramflags)
    ret = AVS_Init(a_Port) 
    return ret
def AVS_UpdateUSBDevices():
    """
    Internally checks the list of connected USB devices and returns the number 
    of devices attached. If AVS_Init() was called with a_Port=-1, the return 
    value also includes the number of ETH devices.
    
    :return: Number of devices found.    
    """
    prototype = func(ctypes.c_int)
    AVS_UpdateUSBDevices = prototype(("AVS_UpdateUSBDevices", lib),)
    ret = AVS_UpdateUSBDevices()
    return ret  
port = 1
deviceID = port
def AVS_Activate(deviceId):
    """
    Activates spectrometer for communication
    
    :param deviceId: The device identifier
    :type deviceId: AvsIdentityType
    :return: AvsHandle, handle to be used in subsequent function calls
    """
    datatype = ctypes.c_byte * 75
    temp = datatype()
    x = 0
    while (x < 9): # 0 through 8
        temp[x] = deviceId.SerialNumber[x]
        x += 1
    temp[9] = 0
    x += 1    
    while (x<74): # 10 through 73
        temp[x] = 0
        x += 1
    temp[74] = int.from_bytes(deviceId.Status, byteorder='big')  #  cannot assign directly here
    prototype = func(ctypes.c_int, ctypes.c_byte * 75)
    paramflags = (1, "deviceId",),
    AVS_Activate = prototype(("AVS_Activate", lib), paramflags)
    ret = AVS_Activate(temp)
    return ret

def AVS_Measure(handle, windowhandle, nummeas):
    """
    Starts measurement on the spectrometer, variant used for Windows messages or polling
    
    :param handle: AvsHandle of the spectrometer
    :param windowhandle: Window handle to notify application measurement result
    data is available. The library sends a Windows message to the window with 
    command WM_MEAS_READY, with SUCCESS, the number of scans that were saved in
    RAM (if enabled), or INVALID_MEAS_DATA as WPARM value and handle as LPARM 
    value. Use on Windows only, 0 to disable.
    :param nummeas: number of measurements to do. -1 is infinite, -2 is used to
    start Dynamic StoreToRam
    :return: SUCCESS = 0 or FAILURE <> 0
    """
    if not (('linux' in sys.platform) or ('darwin' in sys.platform)):
        prototype = func(ctypes.c_int, ctypes.c_int, ctypes.wintypes.HWND, ctypes.c_uint16)
    else:
        prototype = func(ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint16)
    paramflags = (1, "handle",), (1, "windowhandle",), (1, "nummeas")
    AVS_Measure = prototype(("AVS_Measure", lib), paramflags)
    ret = AVS_Measure(handle, windowhandle, nummeas) 
    return ret
  

import subprocess
import psutil
import pygetwindow as gw
##### Opening of AvaSoft #####
def is_application_open(name):
    """Check if there is any running process that contains the given name."""
    for proc in psutil.process_iter(['name']):
        if name.lower() in proc.info['name'].lower():
            try:
                # Focus the window using the process ID and window title
                windows = gw.getWindowsWithTitle("Task Manager")
                if not windows:
                    print(f"No windows found with title containing: {name}")
                for win in windows:
                    print(f"Attempting to activate window: {win.title}")
                    win.activate()
                    win.maximize()  # Optional: Maximize the window
                    return True
            except Exception as e:
                print("Error bringing the window to front:", e)
            return True
    return False




def open_application(path, name):
    """Opens an application if it's not already running."""
    if not is_application_open(name):
        subprocess.Popen(path)
        time.sleep(5)  # Wait for the application to open
    # else:
    #     pyautogui.alert(f'{name} is already running.')

def type_in_application(text):
    """Types a string of text into the open application."""
    pyautogui.typewrite(text, interval=0.1)

if __name__ == "__main__":
    # Path and name of the application you want to check and open (example for Notepad on Windows)
    app_path = 'C:\\Windows\\System32\\notepad.exe'
    app_name = 'notepad.exe'

    # Open or focus the application
    open_application(app_path, app_name)
    type_in_application('Hello, this is a test!')
    pyautogui.press('enter')
    # You can also combine key presses for shortcuts
    # pyautogui.hotkey('ctrl', 's')  # Would typically open the save dialog in many applications
    
    
    
##### Opening Gui ########

# Placeholder functions for Fill_Volt and Fill_Temp
def fill_volt(volt_list):
    # Implementation for filling the voltage list
    pass

def fill_temp(temp_list):
    # Implementation for filling the temperature list
    pass

# Placeholder functions for Init_COM and Init_Gen
def init_com(port):
    # Implementation for initializing the communication port
    pass

def init_gen():
    # Implementation for initializing the generator
    pass

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

        # Initialize pyvisa ResourceManager and the signal generator
        # self.rm = pyvisa.ResourceManager()
        # self.gen_id = self.rm.open_resource('GPIB0::1::INSTR')  # Replace with your resource string

    def initUI(self):
        self.setWindowTitle("PyQt5 GUI")

        # Create the main layout
        self.layout = QVBoxLayout()

        # Status label
        self.label = QLabel('Status: Waiting', self)
        self.layout.addWidget(self.label)

        # Command1 button
        self.button1 = QPushButton('Command1', self)
        self.button1.clicked.connect(self.command1_click)
        self.layout.addWidget(self.button1)

        # Command2 button
        self.button2 = QPushButton('Command2', self)
        self.button2.setEnabled(False)
        self.layout.addWidget(self.button2)

        # Frequency label and text box
        self.label13 = QLabel("Frequency:", self)
        self.text13 = QLineEdit(self)

        # Frequency layout
        freq_layout = QHBoxLayout()
        freq_layout.addWidget(self.label13)
        freq_layout.addWidget(self.text13)
        
        self.layout.addLayout(freq_layout)

        # Set Frequency button
        self.button = QPushButton("Set Frequency", self)
        self.button.clicked.connect(self.set_frequency)
        self.layout.addWidget(self.button)

        # Set the main layout
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)
        self.show()

    def command1_click(self):
        self.button1.setEnabled(False)
        self.button2.setEnabled(True)
        self.label.setText("Initiation")
        
        # Display message box
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Adjust the sensitivity and save the background")
        msg.setWindowTitle("Information")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        
        self.fill_volt([])  # Pass the voltage list (Volt_List)
        self.fill_temp([])  # Pass the temperature list (Temp_List)
        
        port = 1  # sign = 10
        self.init_com(port)
        self.init_gen()

    def set_frequency(self):
        freq = float(self.text13.text())
        wrt_buf = f"APPL:SQU {freq}"
        self.gen_id.write(wrt_buf)

    def fill_volt(self, volt_list):
        # Implement the fill_volt function
        pass

    def fill_temp(self, temp_list):
        # Implement the fill_temp function
        pass

    def init_com(self, port):
        # Implement the init_com function
        pass

    def init_gen(self):
        # Implement the init_gen function
        pass


# Main function to run the application
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
    
   
