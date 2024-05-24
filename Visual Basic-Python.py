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
import gpib_ctypes.gpib
gpib_ctypes.gpib.gpib._load_lib("C:\\Users\\Abeli\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\gpib_ctypes\\gpib")
import pyvisa
import serial
import json


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

AVANTES_path = 'C:\\Windows\\System32\\notepad.exe'
AVANTES_name = 'notepad.exe'

print("Number of Devices connected ",AVS_UpdateUSBDevices())

### Temperature Cycle ###
  

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
    #Opens an application if it's not already running.
    if not is_application_open(name):
        subprocess.Popen(path)
        time.sleep(5)  # Wait for the application to open
    # else:
    #     pyautogui.alert(f'{name} is already running.')

def type_in_application(text):
    """Types a string of text into the open application."""
    pyautogui.typewrite(text, interval=0.1)
       
##### Opening UI ########

# Placeholder functions for Fill_Volt and Fill_Temp

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Set the current Date
        self.da = QDateTime.currentDateTime() 
        
        self.DCmode = False
        self.text_fields = {
            "TemRes": QLineEdit(self),
            "QQ": QLineEdit(self),
            "AvPer": QLineEdit(self),
            "Volt_List": QLineEdit(self),
            "Offset": QLineEdit(self),
            "Temp_List": QLineEdit(self),
            "Fold": QLineEdit(self),
            "BaseName": QLineEdit(self),
            "Temp_Wait": QLineEdit(self),
            "N/A": QLineEdit(self),
            "LastTemp": QLineEdit(self),
            "Accuracy": QLineEdit(self),
            "Frequency": QLineEdit(self),
            "VScalMax": QLineEdit(self),
            "WaitingVoltage": QLineEdit(self),
            "Frequency": QLineEdit(self),
            "AmpGain": QLineEdit(self),
            "WaitV": QLineEdit(self),
        } 
        self.initUI()
        self.load_values()
        self.connect_signals()
        for field in self.text_fields.values():
            field.setFixedSize(200, 20)
    #     # Populate the upper left box with some elements
    #     # self.upper_left_box.addWidget(QLabel('Upper Left Box'))
    #     # self.upper_left_box.addWidget(QPushButton('Button 1'))

        
    #     # Populate the upper right box with some elements
    #     # self.upper_right_box.addWidget(QLabel('Upper Right Box'))
    #     # self.upper_right_box.addWidget(QPushButton('Button 2'))

        
    #     # Populate the lower box with some elements
    #     # Command1 button
    #     # Create the button
    #     self.button1 = QPushButton('Start', self)
    #     # Connect the button's clicked signal to the command1_click method
    #     self.button1.clicked.connect(self.command1_click)
    #     # Add the button to one of the layouts, for example, upper_left_box
    #     self.upper_left_box.addWidget(self.button1)
        
    #     # self.lower_box.addWidget(QLabel('Lower Box'))
    #     # self.lower_box.addWidget(QPushButton('Button 3'))

        
    #     self.show()
        # Create the main layout
        # self.layout = QVBoxLayout()
        
        # Create and set the EndOfProgram label
        # self.EndOfProgram = QLabel('End of Program', self)
        # self.layout.addWidget(self.EndOfProgram)
        # Status label
        # self.Status = QLabel('Status: Waiting', self)
        # self.layout.addWidget(self.Status)
        
   
    def initUI(self):
        self.setWindowTitle("AvaSpec UI")

        # Create main grid layout
        self.grid_layout = QGridLayout()
        
        # Create upper left and right boxes and the lower box
        self.upper_left_box = QVBoxLayout()
        self.upper_right_box = QVBoxLayout()
        self.lower_box = QVBoxLayout()
        
        # Populate the upper left box with some elements
        self.add_text_field_to_layout(self.upper_left_box, "TemRes")
        self.add_text_field_to_layout(self.upper_left_box, "WaitV")
        self.add_text_field_to_layout(self.upper_left_box, "QQ")
        self.add_text_field_to_layout(self.upper_left_box, "AvPer")
        self.add_text_field_to_layout(self.upper_left_box, "Frequency")
        self.add_text_field_to_layout(self.upper_left_box, "VScalMax")
        self.add_text_field_to_layout(self.upper_left_box, "WaitingVoltage")
        self.add_text_field_to_layout(self.upper_left_box, "AmpGain")
        # Command1 button
        self.button1 = QPushButton('Start', self)
        self.button1.clicked.connect(self.command1_click)
        self.upper_left_box.addWidget(self.button1)
        
        # Command2 button
        self.button2 = QPushButton('Stop', self)
        self.button2.clicked.connect(self.command2_click)
        self.upper_left_box.addWidget(self.button2)
        
        # Populate the upper right box with some elements
        self.add_text_field_to_layout(self.upper_right_box, "Volt_List")
        self.add_text_field_to_layout(self.upper_right_box, "Offset")
        self.add_text_field_to_layout(self.upper_right_box, "Temp_List")
        self.add_text_field_to_layout(self.upper_right_box, "Temp_Wait")
        self.add_text_field_to_layout(self.upper_right_box, "N/A")
        self.add_text_field_to_layout(self.upper_right_box, "LastTemp")
        self.add_text_field_to_layout(self.upper_right_box, "Accuracy")
        
        
        # Populate the lower box with some elements
        self.add_text_field_to_layout(self.lower_box, "Fold")
        self.add_text_field_to_layout(self.lower_box, "BaseName")
        
        
        self.Status = QLabel('Status: Waiting', self)
        self.lower_box.addWidget(self.Status)
        self.Status.setStyleSheet("background-color: green;")
        self.Status.setFixedSize(400, 100)  # Set the size of the label
        self.Status.setAlignment(Qt.AlignCenter)

        
        self.upper_left_widget = QWidget()
        self.upper_left_widget.setLayout(self.upper_left_box)
        # self.upper_left_widget.setStyleSheet("") #border: 2px solid red;

        self.upper_right_widget = QWidget()
        self.upper_right_widget.setLayout(self.upper_right_box)
        # self.upper_right_widget.setStyleSheet("") #border: 2px solid green;

        self.lower_widget = QWidget()
        self.lower_widget.setLayout(self.lower_box)
        # self.lower_widget.setStyleSheet("") #border: 2px solid blue;
        
        # Add these boxes to the grid layout
        self.grid_layout.addWidget(self.upper_left_widget, 0, 0)
        self.grid_layout.addWidget(self.upper_right_widget, 0, 1)
        self.grid_layout.addWidget(self.lower_widget, 1, 0, 1, 2)
        
        # Set the grid layout as the central widget's layout
        container = QWidget()
        container.setLayout(self.grid_layout)
        container.setStyleSheet("border: 1px solid black;")
        self.setCentralWidget(container)
        
        self.show()

    def add_text_field_to_layout(self, layout, field_name):
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
        self.text_fields["TemRes"].textChanged.connect(self.text1_change)
        self.text_fields["N/A"].textChanged.connect(self.text2_change)
        self.text_fields["AvPer"].textChanged.connect(self.text3_change)
        self.text_fields["Volt_List"].textChanged.connect(self.text4_change)
        self.text_fields["Offset"].textChanged.connect(self.text5_change)
        self.text_fields["Temp_List"].textChanged.connect(self.text6_change)
        self.text_fields["Fold"].textChanged.connect(self.text7_change)
        self.text_fields["BaseName"].textChanged.connect(self.text8_change)
        self.text_fields["Temp_Wait"].textChanged.connect(self.text9_change)
        self.text_fields["QQ"].textChanged.connect(self.text10_change)
        self.text_fields["LastTemp"].textChanged.connect(self.text11_change)
        self.text_fields["Accuracy"].textChanged.connect(self.text12_change)
        self.text_fields["Frequency"].textChanged.connect(self.text13_change)
        self.text_fields["VScalMax"].textChanged.connect(self.text14_change)
        self.text_fields["WaitingVoltage"].textChanged.connect(self.text16_change)
        self.text_fields["AmpGain"].textChanged.connect(self.text17_change)
        self.text_fields["WaitV"].textChanged.connect(self.text18_change)
    

    def closeEvent(self, event):
        self.save_values()
        super().closeEvent(event)
        
    def command2_click(self):
        # Simulate unloading Form1
        self.exit_flag = True
        # self.close()
        
    def add_labeled_textbox(self, label_text, text_var, change_handler):
        label = QLabel(label_text, self)
        text_var.textChanged.connect(change_handler)
        
        h_layout = QHBoxLayout()
        h_layout.addWidget(label)
        h_layout.addWidget(text_var)
        self.layout.addLayout(h_layout)

    def text1_change(self):
        global TemRes
        TemRes = float(self.text_fields["TemRes"].text())

    def text2_change(self):
        global SomeVar2
        SomeVar2 = float(self.text_fields["N/A"].text())

    def text3_change(self):
        global AvPer
        AvPer = float(self.text_fields["AvPer"].text())

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
        global Fold
        Fold = self.text_fields["Fold"].text()
        
    def text8_change(self):
        global BaseName
        BaseName =self.text_fields["BaseName"].text()

    def text9_change(self):
        global Temp_Wait
        Temp_Wait = float(self.text_fields["Temp_Wait"].text())
        
    def text10_change(self):
        global QQ
        QQ = int(float(self.text_fields["QQ"].text()))

    def text11_change(self):
        global LastTemp
        LastTemp = float(self.text_fields["LastTemp"].text())

    def text12_change(self):
        global Accuracy
        Accuracy = round(float(self.text_fields["Accuracy"].text()), 2)
        
    def text13_change(self):
        Freq = float(self.text_fields["Frequency"].text())
        wrt_buf = f"APPL:SQU {Freq}"
        self.gen_id.write(wrt_buf)

    def text14_change(self):
        global VScalMax
        VScalMax = float(self.text_fields["VScalMax"].text())

    def text16_change(self):
        global WaitingVoltage
        WaitingVoltage = round(float(self.text_fields["WaitingVoltage"].text()), 1)

    def text17_change(self):
        global AmpGain
        AmpGain = round(float(self.text_fields["AmpGain"].text()))

    def text18_change(self):
        global WaitV
        WaitV = float(self.text_fields["WaitV"].text()) * 1000

        
    ### Oscilloscope Control ###
    def Set_WaveForm(self, freq):
        wrt_buf = f"FREQ {freq}"
        self.gen_id.write(wrt_buf)

    def Set_Amplitude(self, amplitude):
        if amplitude != 0:
            if self.DCmode:
                wrt_buf = f"APPL:SQU {self.Freq}"
                self.gen_id.write(wrt_buf)
                wrt_buf = f"VOLT {amplitude}"
                self.gen_id.write(wrt_buf)
                self.DCmode = False
            else:
                wrt_buf = f"VOLT {amplitude}"
                self.gen_id.write(wrt_buf)
        else:
            self.DCmode = True
            wrt_buf = f"APPLy:DC DEF, DEF, {self.Offset}"
            self.gen_id.write(wrt_buf)

    def Set_Offset(self, offset):
        wrt_buf = f"VOLT:OFFS {offset}"
        self.gen_id.write(wrt_buf)

    def Init_Gen(self):
        self.set_offset("0")
        
        
    ### ###
    
    def Waiting(self, min):
        sec = round(min * 60)
        for i in range(1, sec + 1):
            time.sleep(1)
            self.label.setText(f"{self.Mess} ( time left: {round(sec - i)} sec )")
            QApplication.processEvents()

    def Wait_Temp(self):
        self.Mess = "Waiting for Accuracy"
        print('\a')  # Beep
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
        Vmax = 0
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
                    if Voltage[i1] > Vmax:
                        Vmax = Voltage[i1]
            else:
                Voltage[i1] = float(TL)
                if Voltage[i1] > Vmax:
                    Vmax = Voltage[i1]
        self.Num_Volt = i1
        Voltage.append(99999)

    def Fill_Temp(self,tlist):
        TL = tlist.strip()
        p5 = 1
        i5 = 0
        while p5 > 0:
            i5 += 1
            p5 = TL.find(',')
            p6 = TL.find('/')
            if p5 > 0 or p6 > 0:
                if p5 != 0:
                    TL1 = TL[:p5]
                    TL = TL[p5 + 1:]
                else:
                    TL1 = TL
    def Form_Load(self):
        # self.TemRes = float(self.text1.text())
        # self.AvPer = float(self.text3.text())
        # self.Volt_List = self.text4.text()
        # self.Temp_List = self.text6.text()
        # self.Accuracy = round(float(self.text12.text()), 2)
        # self.Offset = float(self.text5.text())
        # self.Temp_Wait = float(self.text9.text())
        # self.VScalMax = float(self.text14.text())
        # self.AmpGain = round(float(self.text17.text()))
        # self.WaitV = float(self.text18.text()) * 1000
        # self.Expire = False
        # self.AST = self.check2.isChecked()
        # self.ASV = self.check4.isChecked()
        x =1

    def form_unload(self):
        sys.exit()
    def log_terminal(self, message):
        self.terminal_output.append(message)
    def Beep():
        print("\a")  # This should produce a beep sound in most terminals

    def Waiting(wait_time):
        print(f"Waiting for {wait_time} seconds...")
        time.sleep(wait_time)
        
    def Set_Amplitude(amplitude):
        print(f"Setting amplitude to {amplitude} V")

    def WaitTemp():
        print("Waiting for temperature to stabilize...")
        time.sleep(1)
    def Crc(message):
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
        return CRC16
    
    def Read_Temp(self):
        ADDRESS = 1
        CODE = 3
        A1_H = 0
        A1_L = 1  # 1- Display; 2-SetPoint
        N_H = 0
        N_L = 1
        TemRes = 1  # Define the temperature resolution variable
        
        ser = serial.Serial('COM1', 9600, timeout=1)  # Adjust the port and baudrate as necessary

        ser.reset_input_buffer()
        time.sleep(0.1)
        
        message = chr(ADDRESS) + chr(CODE) + chr(A1_H) + chr(A1_L) + chr(N_H) + chr(N_L)
        self.Crc(message)
        
        ser.write(message.encode('latin-1'))
        time.sleep(0.1)
        
        mes = ser.read(7)  # Adjust the number of bytes to read if necessary
        
        if len(mes) < 7:
            raise Exception("Incomplete message received")
        
        read_temp = (256 * ord(mes[3]) + ord(mes[4])) / TemRes
        
        ser.close()
        return read_temp
    
    def command1_click(self):
        self.button1.setEnabled(False)
        self.button2.setEnabled(True)
        self.status = QLabel('Initiation', self)
        
        # Establish Connection to AVANTES Software
        AVS_Init(0)
        # Open or focus the application
        open_application(AVANTES_path, AVANTES_name)
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
        self.Init_COM(Port)
        self.Init_Gen()
        self.Freq = float(self.text13.text())
        wrt_buf = f"APPL:SQU {self.Freq}"
        self.gen_id.write(wrt_buf)
        self.Set_Amplitude(Vmax)
        DCmode = False
        FoldName = Fold + BaseName
        it = 0
        TemRes = 100
        ### BEGIN Temperature Cicle ###
        while Temperature[it] != 999:
            SetT = Temperature[it]
            T_Name = FoldName + "T" + str(int((Temperature[it] * TemRes) + 1 / TemRes)).strip()
            Out_Data = T_Name + ".dat"
            self.Beep()
            self.Set_Temp(SetT)
            
            if it != 0:
                self.Waiting(Temp_Wait)
            self.Status = QLabel("Waiting for Temperature", self)
            # self.AVS_Measure()
            CurrentT = self.ARead_Temp
            if abs(SetT - CurrentT) > Accuracy and True:  # Assuming Text12.Text is non-empty
                self.WaitTemp()
            
            # Voltage cycle
            iv = 0
            while Voltage[iv] != 99999:
                if self.exit_flag:
                    print("Exiting function early")
                    self.exit_flag = False
                    return
                self.Set_Amplitude(Voltage[iv] / AmpGain)
                time.sleep(1)  # Sleep for 1000 milliseconds
                time.sleep(WaitV)  # WaitV is already in seconds, no conversion needed
                self.Status = QLabel("V circle", self)
                SSComent = "T" + str(SetT)+"V"+str(Voltage(iv))
                
                pyautogui.hotkey('ctrl', 's')
                time.sleep(2)
                type_in_application(SSComent)
                time.sleep(2)
                pyautogui.hotkey("enter")
                time.sleep(2)
                
                iv += 1
                
        if LastTemp != 0:
            self.Set_Temp(LastTemp)    
        AVS_Done()
        self.Status = QLabel("Program END", self)
        # sys.exit()


# Main function to run the application
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
    
   
