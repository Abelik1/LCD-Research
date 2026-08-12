"""Main function to start Analyser"""

# import subprocess
# import struct

# import ctypes
import json
import sys
import time

# import psutil
import pyautogui
# import pygetwindow as gw
import pyvisa
# import serial

from PyQt5.QtCore import QThread
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from AvaData import AppControl, DirectControl
from avaspec import *
from Generator import ( Generator, Mock_Generator )
from Temp_Probe import Temp_Probe

AVANTES_PATH = "C:\\Program Files (x86)\\AvaSoft8\\avasoft8.exe"
AVANTES_EXE = 'avasoft8.exe'
AVANTEST_NAME = "AvaSoft 8"
# rm = pyvisa.ResourceManager()
# devices = rm.list_resources()
# for device in devices:
#     print(device)

DCmode = False

# print(AVS_Init(0))
# print("Number of Devices connected ",AVS_UpdateUSBDevices())
# print(AVS_GetList())
# deviceId = AVS_GetList()[0]
# AVS_Handle = AVS_Activate(deviceId)
# print(AVS_Handle)
# print(AVS_MeasureCallback(AVS_Handle,None,1))

class MainProgram(QThread):
    """ Opening of MainProgram """
    update_status = pyqtSignal(str)
    finished = pyqtSignal()
    resourceManager = pyvisa.ResourceManager()

    def __init__(self,ui,freq,Volt_List,Temp_List,Accuracy,WaitV,LastTemp,
                Fake_Signal,AmpGain,Folder,BaseName, parent=None):
        super(MainProgram, self).__init__(parent)
        self.ui = ui
        self.Freq = freq
        self.Volt_List =Volt_List
        self.Temp_List =Temp_List
        self.Accuracy = Accuracy
        self.WaitV =WaitV
        self.LastTemp =LastTemp
        self.Fake_Signal=Fake_Signal
        self.AmpGain = AmpGain
        self.Folder = Folder
        self.BaseName = BaseName

        self.Frequency = [0.0] * 300 #300
        self.Voltage = [0.0] * 300 #300
        self.Temperature = [0.0] * 5000 #5000

        self._is_running = True
    def run(self):
        try:
            self.mainprogram()
        finally:
            self.finished.emit()

    def mainprogram(self):
        app_control = AppControl()
        self.ui.save_values()
        self.ui.Form_Load()
        if self.Fake_Signal:
            generator = Mock_Generator()
            temp_probe = Mock_Temp_Probe(ui = self.ui)
        elif self.Fake_Signal:
            generator = Generator(self.resourceManager)
            temp_probe = Temp_Probe(ui=self.ui)

        self.ui.start_btn.setEnabled(False)
        self.ui.stop_btn.setEnabled(True)

        self.ui.Status.setText('Initiation')
        self.ui.Status.update()

        # Establish Connection to AVANTES Software
        if self.Fake_Signal:
            print("connected to AVS_Spec")
            self.ui.Status.setText("Connected to AVS_Spec")
            self.ui.Status.update()
        else:
            # print(AVS_Init(0))
            # print("Number of Devices connected ",AVS_UpdateUSBDevices())
            # print(AVS_GetList())
            # deviceId = AVS_GetList()[0]
            # AVS_Handle = AVS_Activate(deviceId)
            # print("AVS_Handle: ",AVS_Handle)
            pass

        # Open or focus the application
        app_control.open_application(AVANTES_PATH, AVANTES_EXE,AVANTEST_NAME)

        # Display message box
        # msg = QMessageBox()
        # msg.setIcon(QMessageBox.Information)
        # msg.setText("Adjust the sensitivity and save the background")
        # msg.setWindowTitle("Information")
        # msg.setStandardButtons(QMessageBox.Ok)
        # msg.exec_()

        self.Fill_Volt(self.Volt_List)
        self.Fill_Temp(self.Temp_List)
        Port = 1  # sign = 10
        self.Freq = float(self.ui.text_fields["Frequency"].text())
        generator.Set_Freq(self.Freq)
        generator.Set_Amplitude(self.Vmax,self.Freq, DCmode)

        DCmode = False
        FolderName = self.Folder + self.BaseName
        TemRes = 100
        ### BEGIN Temperature Cicle ###
        for SetT in self.Temperature:
            # SetT = Temperature[it]
            T_Name = FolderName + "T" + str(int((SetT * TemRes) + 1 / TemRes)).strip()
            Out_Data = T_Name + ".dat"
            temp_probe.Set_Temp(SetT)

            temp_probe.Wait_Temp(SetT,self.Accuracy)
            self.ui.Status.setText("Waiting for Temperature")
            self.ui.Status.update()
            # self.ui.AVS_Measure()
            CurrentT = temp_probe.Read_Temp()
            temp_probe.Wait_Temp(SetT,self.Accuracy)

            # Voltage cycle
            iv = 0
            for volt in self.Voltage:
                generator.Set_Amplitude(volt / self.AmpGain,self.Freq)   
                if not self.Fake_Signal: 
                    time.sleep(1)  # Sleep for 1000 milliseconds
                    time.sleep(self.WaitV)  # WaitV is already in seconds, no conversion needed
                    self.ui.Status.setText("V circle")
                    self.ui.Status.update()
                    SSComent = "T" + str(SetT)+"V"+str(volt)
                    time.sleep(2)
                    pyautogui.hotkey("alt+F")
                    time.sleep(1)
                    pyautogui.hotkey("S")
                    time.sleep(3)
                    app_control.type_in_application(SSComent)
                    time.sleep(1)
                    pyautogui.hotkey("enter")
                    time.sleep(1)

        if self.LastTemp != 0:
            temp_probe.Set_Temp(self.LastTemp)
        # AVS_Done()
        self.ui.Status.setText("Program END")
        self.ui.Status.update()
        print("Program Done")
        self.ui.start_btn.setEnabled(True)
        self.ui.stop_btn.setEnabled(False)
        # sys.exit()
        
    def Fill_Volt(self,tlist):
        TL = tlist.strip()
        print("Tl:", TL)

        self.Vmax=0
        while TL:
            p1 = TL.find(',')
            if p1 == -1:
                p1 = len(TL)
            
            vl1 = TL[:p1]
            TL = TL[p1 + 1:].strip()
            
            p2 = vl1.find('/')
            if p2 != -1:
                vol1 = float(vl1[:p2])
                vl1 = vl1[p2 + 1:]
                p2 = vl1.find('/')
                vols = float(vl1[:p2])
                vol2 = float(vl1[p2 + 1:])
                
                if vol1 > vol2:
                    vols = -vols
                    
                self.Voltage.extend(range(int(vol1), int(vol2), int(vols)))
            else:
                self.Voltage.append(float(vl1))
            
            if self.Voltage[-1] > self.Vmax:
                self.Vmax = self.Voltage[-1]
        
        self.Num_Volt = len(self.Voltage)

    def Fill_Temp(self,tlist):
        TL = tlist.strip()
        while TL:
            p5 = TL.find(',')
            if p5 == -1:
                p5 = len(TL)
            
            TL1 = TL[:p5]
            TL = TL[p5 + 1:].strip()
            
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
                    self.Temperature.append(vol)
                    vol += tems
            else:
                self.Temperature.append(float(TL1))
        
        self.Num_Temp = len(self.Temperature)

    def stop(self):
        self._is_running = False

##### Opening UI ########

class MainWindow(QMainWindow):
    """Main Controller class"""
    def __init__(self):
        super().__init__()
        self.main_program = None
        self.rm = pyvisa.ResourceManager()
        devices = self.rm.list_resources()
        for device in devices:
            print(device)
        # Set the current Date
        self.da = QDateTime.currentDateTime() 
        self.Fake_Signal = False
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
            # "WaitingVoltage": QLineEdit(self),
            "AmpGain": QLineEdit(self),
            "WaitV": QLineEdit(self),
        }

        self.initUI()
        self.load_values()
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
        self.add_text(self.upper_left_box, "TempRes", "Temperature Resolution") 
        # add_text(location , text_field_name, Label Name)
        self.add_text(self.upper_left_box, "WaitV", "Voltage wait time")
        self.add_text(self.upper_left_box, "Frequency", "Frequency")
        # self.add_text(self.upper_left_box, "WaitingVoltage","")
        self.add_text(self.upper_left_box, "AmpGain","Amp Gain")

        # Populate the upper right box with some elements
        self.add_text(self.upper_right_box, "Volt_List"," Volt List")
        self.add_text(self.upper_right_box, "Offset", "Offset")
        self.add_text(self.upper_right_box, "Temp_List", "Temperature list")
        self.add_text(self.upper_right_box, "Temp_Wait", "Time to wait for Temperature")
        self.add_text(self.upper_right_box, "LastTemp","Last Temperature")
        self.add_text(self.upper_right_box, "Accuracy", "Accuracy")

        for field in self.text_fields.values():
            field.setFixedSize(200, 20)

        # Populate the lower box with some elements
        Folder_Label = QLabel("Folder")
        Folder_Label.setFixedSize(200,20)
        Folder_Field = self.text_fields["Folder"]
        Folder_Field.setFixedSize(300,20)
        self.lower_box.addWidget(Folder_Label)
        self.lower_box.addWidget(Folder_Field)

        BaseName_Label = QLabel("BaseName")
        BaseName_Label.setFixedSize(200,20)
        BaseName_Field = self.text_fields["BaseName"]
        BaseName_Field.setFixedSize(200,20)
        self.lower_box.addWidget(BaseName_Label)
        self.lower_box.addWidget(BaseName_Field)

        BaseName_Label.update()
        BaseName_Field.update()

        self.Status = QLabel('Status: Waiting', self)
        self.lower_box.addWidget(self.Status)
        self.Status.setStyleSheet("background-color: green;")
        self.Status.setFixedSize(400, 100)  # Set the size of the label
        self.Status.setAlignment(Qt.AlignCenter)

        # Start button
        self.start_btn = QPushButton('Start', self)
        self.start_btn.setFixedSize(QSize(100, 50))  # Set button size
        self.start_btn.setStyleSheet("background-color: green; color: white;")
        self.start_btn.clicked.connect(self.start_command)
        self.upper_left_box.addWidget(self.start_btn)
        self.start_btn.setEnabled(True)


        # Stop button
        self.stop_btn = QPushButton('Stop', self)
        self.stop_btn.setFixedSize(QSize(100, 50))  # Set button size
        self.stop_btn.setStyleSheet("background-color: red; color: white;")
        self.stop_btn.clicked.connect(self.stop_command)
        self.upper_left_box.addWidget(self.stop_btn)
        self.stop_btn.setEnabled(False)

        # Fake Signal button
        self.checkbox = QCheckBox('Fake Signal', self)
        self.checkbox.stateChanged.connect(self.checkbox_state_changed)
        self.upper_left_box.addWidget(self.checkbox)

        # Create and set up the upper left widget
        self.upper_left_widget = QWidget()
        self.upper_left_widget.setLayout(self.upper_left_box)
        self.add_group_box_with_title(self.upper_left_widget, self.grid_layout, 
                                      'Upper Left Box', 0, 0)

        # Create and set up the upper right widget
        self.upper_right_widget = QWidget()
        self.upper_right_widget.setLayout(self.upper_right_box)
        self.add_group_box_with_title(self.upper_right_widget, self.grid_layout, 
                                      'Upper Right Box', 0, 1)

        # Create and set up the lower widget
        self.lower_widget = QWidget()
        self.lower_widget.setLayout(self.lower_box)
        self.add_group_box_with_title(self.lower_widget, self.grid_layout, 
                                      'Lower Box', 1, 0, 1, 2)

        # Set the grid layout as the central widget's layout
        container = QWidget()
        container.setLayout(self.grid_layout)
        # container.setStyleSheet("border: 1px solid black;")
        self.setCentralWidget(container)

        self.show()

    def start_command(self):
        if self.main_program is None:
            self.main_program = MainProgram(self,self.Freq, self.Volt_List,self.Temp_List,
                                            self.Accuracy,self.WaitV,self.LastTemp,
                                            self.Fake_Signal,self.AmpGain,self.Folder,self.BaseName)
            self.main_program.finished.connect(self.command_finished)
            self.main_program.start()
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.start_btn.setStyleSheet("background-color: grey; color: white;")
            self.Status.setText("Running command...")
            self.Status.update()

    def stop_command(self):
        if self.main_program is not None:
            self.main_program.stop()
            self.main_program.wait()
            self.main_program = None
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.Status.setText("Command stopped")

    def command_finished(self):
        self.main_program = None
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.start_btn.setStyleSheet("background-color: green; color: white;")
        self.Status.setText("Command finished")

    def closeEvent(self, event):
        self.save_values()
        super().closeEvent(event)

    def checkbox_state_changed(self, state):
        if state == 2:  # Checked
            print('Checkbox checked')
            self.Fake_Signal = True      
        else:  # Unchecked
            print('Checkbox unchecked')
            self.Fake_Signal = False 

    def add_group_box_with_title(self, widget, layout, title, row, col, rowspan=1, colspan=1):
        group_box =QGroupBox(title)
        group_layout = QVBoxLayout()
        group_layout.addWidget(widget)
        group_box.setLayout(group_layout)
        layout.addWidget(group_box, row, col, rowspan, colspan)

    def add_text(self, layout, field_name, name):
        if field_name in self.text_fields:
            label = QLabel(name)
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

    def Form_Load(self):

        if self.text_fields["TempRes"].text() != "": 
            self.TemRes = float(self.text_fields["TempRes"].text())
        if self.text_fields["Volt_List"].text() != "": 
            self.Volt_List = self.text_fields["Volt_List"].text()
        if self.text_fields["Temp_List"].text() != "": 
            self.Temp_List = self.text_fields["Temp_List"].text()
        if self.text_fields["Accuracy"].text() != "": 
            self.Accuracy = round(float(self.text_fields["Accuracy"].text()), 2)
        if self.text_fields["Offset"].text() != "": 
            self.Offset = float(self.text_fields["Offset"].text())
        if self.text_fields["Temp_Wait"].text() != "": 
            self.Temp_Wait = float(self.text_fields["Temp_Wait"].text())
        if self.text_fields["Temp_Wait"].text() != "": 
            self.LastTemp = float(self.text_fields["LastTemp"].text())
        if self.text_fields["AmpGain"].text() != "": 
            self.AmpGain = round(float(self.text_fields["AmpGain"].text()))
        if self.text_fields["WaitV"].text() != "": 
            self.WaitV = float(self.text_fields["WaitV"].text())
        if self.text_fields["Frequency"].text() != "": 
            self.Freq = float(self.text_fields["Frequency"].text())
        if self.text_fields["Folder"].text() != "": 
            self.Folder = self.text_fields["Folder"].text()
        if self.text_fields["BaseName"].text() != "": 
            self.BaseName = self.text_fields["BaseName"].text() 

    def form_unload(self):
        sys.exit()

def main():
    """ Main function to run the application """
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
