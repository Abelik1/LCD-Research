import pyautogui
import subprocess
import time
import numpy as np
import sys
import ctypes
import struct
from PyQt5.QtWidgets import *
from avaspec import *
from PyQt5.QtCore import *
import pyvisa
import serial
import json


# print("This is the Temperature: ",Read_Temp())

dev_Osc, Command, param, Out_File, Out_Data, Volt_List, Temp_List, ReadBuffer = "", "", "", "", "", "", "", ""
# SSComment = ""
Frequency = [0.0] * 3 #300
Voltage = [0.0] * 3 #300
Temperature = [0.0] * 3 #5000
Freq, Amplitude, Offset, AmpGain, AvPer, VScal, VScalMax, Vmax = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
Temp_Wait, LastTemp, WaitV, WaitingVoltage, Accuracy, CurrentT, SetT = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
# Num_Volt, Num_Temp, TemRes = 0, 0, 0
Fast, AST, ASV, Expire, DCmode = False, False, False, False, False

AVANTES_path = "C:\\Program Files (x86)\\AvaSoft8\\avasoft8.exe"
Avantes_exe = 'avasoft8.exe'
Avantes_name = "AvaSoft 8"
# rm = pyvisa.ResourceManager()
# devices = rm.list_resources()
# for device in devices:
#     print(device)
# print(Read_Temp())
# Set_Temp(30.0)
# time.sleep(10)
# print(Read_Temp())
DCmode = False

# Init_Gen()
# Set_Freq(1000)
# Set_Amplitude(2.1,1000)



# Set_Freq(120)
# Set_Amplitude(0.2,110)         
# print(AVS_Init(0))
# print("Number of Devices connected ",AVS_UpdateUSBDevices())
# print(AVS_GetList())
# deviceId = AVS_GetList()[0]
# AVS_Handle = AVS_Activate(deviceId)
# print(AVS_Handle)
# print(AVS_MeasureCallback(AVS_Handle,None,1))
### Temperature Cycle ###
  

import subprocess
import psutil
import pygetwindow as gw
##### Opening of AvaSoft #####

       
##### Opening UI ########

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.rm = pyvisa.ResourceManager()
        devices = self.rm.list_resources()
        for device in devices:
            print(device)
        self.exit_flag = False
        # Set the current Date
        self.da = QDateTime.currentDateTime() 
        
        self.DCmode = False
        self.text_fields = {
            "TempRes": QLineEdit(self),
            "Volt_List": QLineEdit(self),
            "Offset": QLineEdit(self),
            "Temp_List": QLineEdit(self), 
            "Folder": QLineEdit(self),
            "BaseName": QLineEdit(self),
            "Temp_Wait": QLineEdit(self), # Used Once in the Temp loop
            "LastTemp": QLineEdit(self),
            "Accuracy": QLineEdit(self),
            "Frequency": QLineEdit(self),
            "WaitingVoltage": QLineEdit(self),
            "AmpGain": QLineEdit(self),
            "WaitV": QLineEdit(self),
        } 
        self.initUI()
        self.load_values()
        self.connect_signals()
        for field in self.text_fields.values():
            field.setFixedSize(200, 20)
        self.Form_Load()      
   
    def initUI(self):
        self.setGeometry(300, 300, 900, 400)
        self.setWindowTitle("AvaSpec UI")

        # Create main grid layout
        self.grid_layout = QGridLayout()
        
        # Create upper left and right boxes and the lower box
        self.upper_left_box = QVBoxLayout()
        self.upper_right_box = QVBoxLayout()
        self.lower_box = QVBoxLayout()
        
        # Populate the upper left box with some elements
        self.add_text(self.upper_left_box, "TempRes")
        self.add_text(self.upper_left_box, "WaitV")
        self.add_text(self.upper_left_box, "Frequency")
        self.add_text(self.upper_left_box, "WaitingVoltage")
        self.add_text(self.upper_left_box, "AmpGain")
        
        
        # Populate the upper right box with some elements
        self.add_text(self.upper_right_box, "Volt_List")
        self.add_text(self.upper_right_box, "Offset")
        self.add_text(self.upper_right_box, "Temp_List")
        self.add_text(self.upper_right_box, "Temp_Wait")
        self.add_text(self.upper_right_box, "LastTemp")
        self.add_text(self.upper_right_box, "Accuracy")
        
        
        # Populate the lower box with some elements
        self.add_text(self.lower_box, "Folder")
        self.add_text(self.lower_box, "BaseName")
        
        
        self.Status = QLabel('Status: Waiting', self)
        self.lower_box.addWidget(self.Status)
        self.Status.setStyleSheet("background-color: green;")
        self.Status.setFixedSize(400, 100)  # Set the size of the label
        self.Status.setAlignment(Qt.AlignCenter)
        
        # Command1 button
        self.button1 = QPushButton('Start', self)
        self.button1.setFixedSize(QSize(100, 50))  # Set button size
        self.button1.setStyleSheet("background-color: green; color: white;")
        self.button1.clicked.connect(self.command1_click)
        self.upper_left_box.addWidget(self.button1)
        self.button1.setEnabled(True)
        
        # Command2 button
        self.button2 = QPushButton('Stop', self)
        self.button2.setFixedSize(QSize(100, 50))  # Set button size
        self.button2.setStyleSheet("background-color: red; color: white;")
        self.button2.clicked.connect(self.command2_click)
        self.upper_left_box.addWidget(self.button2)
        self.button2.setEnabled(False)
        
        # Fake Signal button
        self.checkbox = QCheckBox('Fake Signal', self)
        self.checkbox.stateChanged.connect(self.checkbox_state_changed)
        self.upper_left_box.addWidget(self.checkbox)
        
        # Create and set up the upper left widget
        self.upper_left_widget = QWidget()
        self.upper_left_widget.setLayout(self.upper_left_box)
        self.add_group_box_with_title(self.upper_left_widget, self.grid_layout, 'Upper Left Box', 0, 0)

        # Create and set up the upper right widget
        self.upper_right_widget = QWidget()
        self.upper_right_widget.setLayout(self.upper_right_box)
        self.add_group_box_with_title(self.upper_right_widget, self.grid_layout, 'Upper Right Box', 0, 1)

        # Create and set up the lower widget
        self.lower_widget = QWidget()
        self.lower_widget.setLayout(self.lower_box)
        self.add_group_box_with_title(self.lower_widget, self.grid_layout, 'Lower Box', 1, 0, 1, 2)

        # Set the grid layout as the central widget's layout
        container = QWidget()
        container.setLayout(self.grid_layout)
        # container.setStyleSheet("border: 1px solid black;")
        self.setCentralWidget(container)
        
        self.show()
        
    def closeEvent(self, event):
        self.save_values()
        super().closeEvent(event)
        
    def command2_click(self):
        # Simulate unloading Form1
        self.exit_flag = True
        self.close()   
    def checkbox_state_changed(self, state):
        if state == 2:  # Checked
            print('Checkbox checked')
            self.Fake_Signal = True
            # Add your code to handle the checked state
        else:  # Unchecked
            print('Checkbox unchecked')
            self.Fake_Signal = False
            # Add your code to handle the unchecked state 
    def add_group_box_with_title(self, widget, layout, title, row, col, rowspan=1, colspan=1):
        group_box =QGroupBox(title)
        group_layout = QVBoxLayout()
        group_layout.addWidget(widget)
        group_box.setLayout(group_layout)
        layout.addWidget(group_box, row, col, rowspan, colspan)
        
    def add_text(self, layout, field_name):
        if field_name in self.text_fields:
            label = QLabel(field_name)
            field = self.text_fields[field_name]
            layout.addWidget(label)
            layout.addWidget(field)

    def save_values(self):
        values = {label: field.text() for label, field in self.text_fields.items()}
        with open("values.json", "w") as f:
            json.dump(values, f)

    def load_values(self):
        try:
            with open("values.json", "r") as f:
                values = json.load(f)
                for label, value in values.items():
                    if label in self.text_fields:
                        self.text_fields[label].setText(value)
        except FileNotFoundError:
            pass
    def connect_signals(self):
        self.text_fields["TempRes"].textChanged.connect(self.text1_change)
        self.text_fields["Volt_List"].textChanged.connect(self.text4_change)
        self.text_fields["Offset"].textChanged.connect(self.text5_change)
        self.text_fields["Temp_List"].textChanged.connect(self.text6_change)
        self.text_fields["Folder"].textChanged.connect(self.text7_change)
        self.text_fields["BaseName"].textChanged.connect(self.text8_change)
        self.text_fields["Temp_Wait"].textChanged.connect(self.text9_change)
        self.text_fields["LastTemp"].textChanged.connect(self.text11_change)
        self.text_fields["Accuracy"].textChanged.connect(self.text12_change)
        self.text_fields["Frequency"].textChanged.connect(self.text13_change)
        self.text_fields["WaitingVoltage"].textChanged.connect(self.text16_change)
        self.text_fields["AmpGain"].textChanged.connect(self.text17_change)
        self.text_fields["WaitV"].textChanged.connect(self.text18_change)

    def text1_change(self):
        global TemRes
        TemRes = float(self.text_fields["TempRes"].text())

    def text4_change(self):
        global Volt_List
        Volt_List = self.text_fields["Volt_List"].text()

    def text5_change(self):
        global Offset
        Offset = float(self.text_fields["Offset"].text())

    def text6_change(self):
        global Temp_List
        Temp_List = self.text_fields["Temp_List"].text()

    def text7_change(self):
        global Folder
        Folder = self.text_fields["Folder"].text()
        
    def text8_change(self):
        global BaseName
        BaseName =self.text_fields["BaseName"].text()

    def text9_change(self):
        global Temp_Wait
        Temp_Wait = float(self.text_fields["Temp_Wait"].text())

    def text11_change(self):
        global LastTemp
        LastTemp = float(self.text_fields["LastTemp"].text())

    def text12_change(self):
        global Accuracy
        Accuracy = round(float(self.text_fields["Accuracy"].text()), 2)
        
    def text13_change(self):
        global Freq
        Freq = float(self.text_fields["Frequency"].text())

    def text16_change(self):
        global WaitingVoltage
        WaitingVoltage = round(float(self.text_fields["WaitingVoltage"].text()), 1)

    def text17_change(self):
        global AmpGain
        AmpGain = round(float(self.text_fields["AmpGain"].text()))

    def text18_change(self):
        global WaitV
        WaitV = float(self.text_fields["WaitV"].text())

    ### Window Control ###
    # def is_application_open(self,name):
    #     """Check if there is any running process that contains the given name."""
    #     for proc in psutil.process_iter(['name']):
    #         if name.lower() in proc.info['name'].lower():
    #             try:
    #                 # Focus the window using the process ID and window title
    #                 windows = gw.getWindowsWithTitle("Task Manager")
    #                 if not windows:
    #                     print(f"No windows found with title containing: {name}")
    #                 for win in windows:
    #                     print(f"Attempting to activate window: {win.title}")
    #                     win.activate()
    #                     win.maximize()  # Optional: Maximize the window
    #                     return True
    #             except Exception as e:
    #                 print("Error bringing the window to front:", e)
    #             return True
    #     return False

    # def open_application(self,path, name):
    #     #Opens an application if it's not already running.
    #     if not self.is_application_open(name):
    #         subprocess.Popen(path)
    #         time.sleep(5)  # Wait for the application to open
    #     # else:
    #     #     pyautogui.alert(f'{name} is already running.')

    # def type_in_application(self,text):
    #     """Types a string of text into the open application."""
    #     pyautogui.typewrite(text, interval=0.1)   
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
    
    def Waiting(self, sec):
        for i in range(1, sec + 1):
            time.sleep(1)
            self.label.setText(f"{self.Mess} ( time left: {round(sec - i)} sec )")
            QApplication.processEvents()

    def Wait_Temp(self):
        self.Mess = "Waiting for Accuracy"
        i = 0
        while abs(self.SetT - self.CurrentT) > self.Accuracy:
            time.sleep(1)
            self.label.setText(f"{self.Mess} {i} sec")
            QApplication.processEvents()
            i += 1
            self.CurrentT = self.read_temp()

    def Fill_Volt(self,tlist):
        TL = tlist.strip()
        print("Tl", TL)
        p1 = 1
        self.Vmax = 0
        i1 = 0
        while p1 > 0:
            i1 += 1
            p1 = TL.find(',') # Get position of next comma
            p2 = TL.find('/') # Get position of next "/"
            if p1 > 0 or p2 > 0:
                if p1 != 0:
                    vl1 = TL[:p1]
                    TL = TL[p1 + 1:]
                else:
                    vl1 = TL
                p2 = vl1.find('/') # Get position of next "/"
                if p2 != 0:
                    vol1 = float(vl1[:p2])
                    vl1 = vl1[p2 + 1:]
                    p2 = vl1.find('/')
                    vols = float(vl1[:p2])
                    vol2 = float(vl1[p2 + 1:])
                    if vol1 > vol2:
                        vols = -vols
                    for vol in range(int(vol1), int(vol2), int(vols)):
                        Voltage.append(vol)
                        i1 += 1
                    i1 -= 1
                else:
                    Voltage.append(float(vl1))
                    if Voltage[i1] > self.Vmax:
                        self.Vmax = Voltage[i1]
            else:
                Voltage[i1] = float(TL)
                if Voltage[i1] > self.Vmax:
                    self.Vmax = Voltage[i1]
        self.Num_Volt = i1
        Voltage.append(99999)

    def Fill_Temp(self,tlist):
        # TL = tlist.strip()
        # p5 = 1
        # i5 = 0
        # while p5 > 0:
        #     i5 += 110.0
        
        #     p5 = TL.find(',')
        #     p6 = TL.find('/')
        #     if p5 > 0 or p6 > 0:
        #         if p5 != 0:
        #             TL1 = TL[:p5]
        #             TL = TL[p5 + 1:]
        #         else:
        #             TL1 = TL
        Num_Temp = 0
    
        TL = tlist.strip()
        i5 = 0
        
        while TL:
            i5 += 1
            p5 = TL.find(',')
            p6 = TL.find('/')
            
            if p5 > 0 or p6 > 0:
                if p5 != -1:
                    TL1 = TL[:p5]
                    TL = TL[p5 + 1:]
                else:
                    TL1 = TL
                    TL = ""
                
                p6 = TL1.find('/')
                if p6 != -1:
                    tem1 = float(TL1[:p6])
                    TL1 = TL1[p6 + 1:]
                    p6 = TL1.find('/')
                    tems = float(TL1[:p6])
                    tem2 = float(TL1[p6 + 1:])
                    if tem1 > tem2:
                        tems = -tems
                    vol = tem1
                    while (vol <= tem2 and tems > 0) or (vol >= tem2 and tems < 0):
                        Temperature[i5] = vol
                        i5 += 1
                        vol += tems
                    i5 -= 1
                else:
                    Temperature[i5] = float(TL1)
            else:
                Temperature[i5] = float(TL)
                TL = ""
        
        Num_Temp = i5
        Temperature.append(999)
                
    def Form_Load(self):
        global TemRes,Volt_List,Accuracy,Offset,Temp_List,Temp_Wait,AmpGain,WaitV,Freq,Folder,BaseName
        if self.text_fields["TempRes"].text() != "": 
            TemRes = float(self.text_fields["TempRes"].text())
        if self.text_fields["Volt_List"].text() != "": 
            Volt_List = self.text_fields["Volt_List"].text()
        if self.text_fields["Temp_List"].text() != "": 
            Temp_List = self.text_fields["Temp_List"].text()
        if self.text_fields["Accuracy"].text() != "": 
            Accuracy = round(float(self.text_fields["Accuracy"].text()), 2)
        if self.text_fields["Offset"].text() != "": 
            Offset = float(self.text_fields["Offset"].text())
        if self.text_fields["Temp_Wait"].text() != "": 
            Temp_Wait = float(self.text_fields["Temp_Wait"].text())
        if self.text_fields["AmpGain"].text() != "": 
            AmpGain = round(float(self.text_fields["AmpGain"].text()))
        if self.text_fields["WaitV"].text() != "": 
            WaitV = float(self.text_fields["WaitV"].text())
        if self.text_fields["Frequency"].text() != "": 
            Freq = float(self.text_fields["Frequency"].text())
        if self.text_fields["Folder"].text() != "": 
            Folder = self.text_fields["Folder"].text()
        if self.text_fields["BaseName"].text() != "": 
            BaseName = self.text_fields["BaseName"].text() 



    def form_unload(self):
        sys.exit()
        
    def Waiting(self,wait_time):
        print(f"Waiting for {wait_time} seconds...")
        self.Status = QLabel(f"Waiting for {wait_time} seconds...")
        time.sleep(wait_time)

    def WaitTemp(self):
        global Temp_Wait
        print("Waiting for temperature to stabilize...")
        self.Status.setText("Waiting for temperature to stabilize...")
        time.sleep(Temp_Wait)
        
    def Crc(self,message):
        CRC16 = 65535
        for c in message:
            CRC16 ^= ord(c)
            for _ in range(8):
                if CRC16 % 2:
                    CRC16 = (CRC16 >> 1) ^ 40961
                else:
                    CRC16 >>= 1
        
        CRCH = CRC16 >> 8
        CRCL = CRC16 & 255
        message += chr(CRCL) + chr(CRCH) + "xyz"
        print(CRC16,"CRC16")
        # return CRC16
        return message
    
    def Read_Temp(self):
        if self.Fake_Signal == False:
            ADDRESS = 1
            CODE = 3
            A1_H = 0
            A1_L = 1  # 1- Display; 2-SetPoint
            N_H = 0
            N_L = 1
            TemRes = 100  # Define the temperature resolution variable
            
            ser = serial.Serial('COM1', 9600, timeout=1)  # Adjust the port and baudrate as necessary
            ser.reset_input_buffer()
            time.sleep(0.1)
            
            message = chr(ADDRESS) + chr(CODE) + chr(A1_H) + chr(A1_L) + chr(N_H) + chr(N_L)
            message = self.Crc(message)
            
            ser.write(message.encode('latin-1'))
            time.sleep(0.1)
            mes = ser.read(7)  # Adjust the number of bytes to read if necessary
            if len(mes) < 7:
                raise Exception("Incomplete message received for Temperature")
            
            read_temp = (256 * (mes[3]) + (mes[4])) / TemRes
            
            ser.close()
            return read_temp
        else:
            return 20.0
            
    
    def Set_Temp(self,temp):
        if self.Fake_Signal == False:
            TemRes=100
            temp= int(TemRes*temp)
            ADDRESS =1
            CODE = 6
            A_MSB = 0
            A_LSB = 2
            V_MSB = temp // 256
            V_LSB = temp % 256
            
            message = chr(ADDRESS) + chr(CODE) + chr(A_MSB) + chr(A_LSB) + chr(V_MSB) + chr(V_LSB)
            message = self.Crc(message)
            
            ser = serial.Serial('COM1', 9600, timeout=1)  # Adjust the port and baudrate as necessary

            ser.write(message.encode("latin-1"))
            time.sleep(0.2)
            ser.close()
            return 1
        else:
            return 1
    
    def Set_Offset(self,offset):
        if self.Fake_Signal == False:
            command = f"VOLT:OFFS {offset}\n"
            self.send_command(command)
        else:
            pass
        
    def Init_Gen(self):
        # global ser
        B_G = 0
        P_G = 10
        N_G = 0
        T_G = 0
        E1_G = 1
        E2_G = 0
        # gpib_address = f"FPIB{B_G}::{P_G}::{N_G}::INSTR"
        gpib_address = "GPIB0::10::INSTR"
        if self.Fake_Signal == True:
            print("connected to generator")
        else:
            self.gen = self.rm.open_resource(gpib_address)

        # ser = serial.Serial("COM1",9600,timeout = 3)
        self.Set_Offset("0")
        
    def send_command(self,command):
        if self.Fake_Signal == False:
            if self.gen is not None:
                self.gen.write(command)
            else:
                raise Exception("No connection on GPIB")
        else:
            pass    
    def Set_Waveform(self,form):
        if self.Fake_Signal == False:
            command = f"FUNC:SHAP {form}\n"
            self.send_command(command)
        else:
            pass
    def Set_Freq(self,freq):
        if self.Fake_Signal == False:
            command = f"FREQ {freq}"
            self.send_command(command)
        else:
            pass
    def Set_Amplitude(self,amplitude, freq):
        if self.Fake_Signal == False:
            global DCmode
            if amplitude != 0:
                if DCmode:
                    command = f"APPL:SQU {freq}\n"
                    self.send_command(command)
                    command = f"VOLT {amplitude}\n"
                    self.send_command(command)
                    DCmode = False
                else:
                    command = f"VOLT {amplitude}\n"
                    self.send_command(command)
            else:
                DCmode = True
                command = f"APPLy:DC DEF, DEF, O\n"
                self.send_command(command)
        else:
            pass
            
    ### Run MAIN Program ###        
    def command1_click(self):
        self.save_values()
        global TemRes,Volt_List,Accuracy,Offset,Temp_List,Temp_Wait,AmpGain,WaitV,Freq
        self.button1.setEnabled(False)
        self.button2.setEnabled(True)
        self.Status.setText('Initiation')
        # Establish Connection to AVANTES Software
        if self.Fake_Signal == True:
            print("connected to AVS_Spec")
            self.Status.setText("Connected to AVS_Spec")
        else:
            print(AVS_Init(0))
            print("Number of Devices connected ",AVS_UpdateUSBDevices())
            print(AVS_GetList())
            deviceId = AVS_GetList()[0]
            AVS_Handle = AVS_Activate(deviceId)
            print("AVS_Handle: ",AVS_Handle)
            
        # Open or focus the application
        self.open_application(AVANTES_path, Avantes_exe,Avantes_name)
        # type_in_application('Hello, this is a test!') ## Commented out
        # pyautogui.press('enter')
        # You can also combine key presses for shortcuts
        # pyautogui.hotkey('ctrl', 's')  # Would typically open the save dialog in many applications
        
        # Display message box
        # msg = QMessageBox()
        # msg.setIcon(QMessageBox.Information)
        # msg.setText("Adjust the sensitivity and save the background")
        # msg.setWindowTitle("Information")
        # msg.setStandardButtons(QMessageBox.Ok)
        # msg.exec_()
        
        self.Fill_Volt(Volt_List)
        self.Fill_Temp(Temp_List)
        Port = 1  # sign = 10
        self.Init_Gen()
        self.Freq = float(self.text_fields["Frequency"].text())
        self.Set_Freq(self.Freq)
        self.Set_Amplitude(self.Vmax,self.Freq)
         
        DCmode = False
        FolderName = Folder + BaseName
        it = 0
        TemRes = 100
        ### BEGIN Temperature Cicle ###
        while Temperature[it] != 999:
            SetT = Temperature[it]
            T_Name = FolderName + "T" + str(int((Temperature[it] * TemRes) + 1 / TemRes)).strip()
            Out_Data = T_Name + ".dat"
            self.Set_Temp(SetT)
            
            if it != 0:
                self.Waiting(Temp_Wait)
            self.Status.setText("Waiting for Temperature")
            # self.AVS_Measure()
            CurrentT = self.Read_Temp()
            if abs(SetT - CurrentT) > Accuracy and True: 
                self.WaitTemp()
            
            # Voltage cycle
            iv = 0
            while Voltage[iv] != 99999:
                if self.exit_flag:
                    print("Exiting function early")
                    self.exit_flag = False
                    return
                self.Set_Amplitude(Voltage[iv] / AmpGain,self.Freq)
                if self.Fake_Signal == False:
                    
                    time.sleep(1)  # Sleep for 1000 milliseconds
                    time.sleep(WaitV)  # WaitV is already in seconds, no conversion needed
                    self.Status.setText("V circle")
                    SSComent = "T" + str(SetT)+"V"+str(Voltage[iv])
                    
                    pyautogui.hotkey('ALT+F', 'S',"E")
                    time.sleep(1)
                    self.type_in_application(SSComent)
                    time.sleep(1)
                    pyautogui.hotkey("enter")
                    time.sleep(1)
                
                iv += 1
            it+=1    
        if LastTemp != 0:
            self.Set_Temp(LastTemp)    
        AVS_Done()
        self.Status.setText("Program END")
        print("Program Done")
        self.Status.setText("Program END")
        self.button1.setEnabled(True)
        self.button2.setEnabled(False)
        # sys.exit()


# Main function to run the application
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
    
   
