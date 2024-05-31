# import subprocess
# import struct

# import ctypes
import json
import sys
import time
# from qwt import *
# from plotpy import *
# import psutil
import pyautogui
# import pygetwindow as gw
import pyvisa


from PyQt5.QtCore import QThread
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from avaspec import *

from AvaData import *
# from avaspec import *
from Generator import *
from Temp_Probe import *

from ast import Str
from inspect import ArgSpec
import os
import platform
import sys
import time
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from avaspec import *
import globals
import qtdemo
import analog_io_demo
import digital_io_demo
import eeprom_demo
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

        self.Frequency = []  #300
        self.Voltage = [] #300
        self.Temperature = []  #5000

        self._is_running = True
    def run(self):
        try:
            self.mainprogram()
        finally:
            self.finished.emit()

    def mainprogram(self):
        while self._is_running:
            app_control = AppControl()
            self.ui.save_values()
            self.ui.Form_Load()
            if self.Fake_Signal:
                generator = Mock_Generator()
                temp_probe = Mock_Temp_Probe(ui = self.ui)
            elif not self.Fake_Signal:
                generator = Generator(self.resourceManager)
                temp_probe = Temp_Probe(ui=self.ui)
            self.ui.start_btn.setEnabled(False)
            self.ui.stop_btn.setEnabled(True)
            if not self._is_running:
                self.ui.Status.setText("Stopping...")
                self.ui.Status.update()
                break
            self.ui.Status.setText('Initiation')
            self.ui.Status.update()

            # Establish Connection to AVANTES Software
            if self.Fake_Signal:
                print("connected to AVS_Spec")
                self.ui.Status.setText("Connected to AVS_Spec")
                self.ui.Status.update()

            # Open or focus the application
            app_control.open_application(AVANTES_PATH, AVANTES_EXE,AVANTEST_NAME)
            if not self._is_running:
                self.ui.Status.setText("Stopping...")
                self.ui.Status.update()
                break
            if self.ui.Auto:
                if app_control.is_application_open(AVANTEST_NAME):
                    time.sleep(0.5)
                    pyautogui.press("ENTER")
                    time.sleep(0.5)
                else:
                    pyautogui.press("down")
                    time.sleep(0.5)
                    pyautogui.press("right")
                    time.sleep(0.5)
                    if not self._is_running:
                        self.ui.Status.setText("Stopping...")
                        self.ui.Status.update()
                        break
                    pyautogui.press("ENTER")
                    time.sleep(0.5)
                    pyautogui.press("ENTER")
                    time.sleep(0.5)
            if not self._is_running:
                self.ui.Status.setText("Stopping...")
                self.ui.Status.update()
                break
            DCmode = False
            self.Fill_Volt(self.Volt_List)
            self.Fill_Temp(self.Temp_List)
            print(self.Voltage)
            print(self.Temperature)
            Port = 1  # sign = 10
            self.Freq = float(self.ui.text_fields["Frequency"].text())
            generator.Set_Freq(self.Freq)
            generator.Set_Amplitude(self.Vmax,self.Freq, DCmode)

            
            FolderName = self.Folder + self.BaseName
            TemRes = 100
            ### BEGIN Temperature Cicle ###
            for SetT in self.Temperature:
                # SetT = Temperature[it]
                T_Name = FolderName + "T" + str(int((SetT * TemRes) + 1 / TemRes)).strip()
                Out_Data = T_Name + ".dat"
                temp_probe.Set_Temp(SetT)
                if not self._is_running:
                    self.ui.Status.setText("Stopping...")
                    self.ui.Status.update()
                    break
                temp_probe.Wait_Temp(SetT,self.Accuracy,self._is_running)
                if not self._is_running:
                    self.ui.Status.setText("Stopping...")
                    self.ui.Status.update()
                    break
                self.ui.Status.setText("Waiting for Temperature")
                self.ui.Status.update()
                # self.ui.AVS_Measure()
                CurrentT = temp_probe.Read_Temp()
                temp_probe.Wait_Temp(SetT,self.Accuracy,self._is_running)
                if not self._is_running:
                    self.ui.Status.setText("Stopping...")
                    self.ui.Status.update()
                    break
                # self.ui.Temp_Label.setText(f"Current Temp: {CurrentT}")
                # self.ui.Temp_Label.update()
                # Voltage cycle
                iv = 0
                for volt in self.Voltage:
                    generator.Set_Amplitude(volt / self.AmpGain,self.Freq,DCmode)   
                    if not self.Fake_Signal: 
                        print("SAVING")
                        if not self._is_running:
                            self.ui.Status.setText("Stopping...")
                            self.ui.Status.update()
                            break
                        app_control.open_application(AVANTES_PATH, AVANTES_EXE,AVANTEST_NAME)
                        time.sleep(1)  # Sleep for 1000 milliseconds
                        time.sleep(self.WaitV)  # WaitV is already in seconds, no conversion needed
                        self.ui.Status.setText("V circle")
                        # self.ui.Temp_Label.setText(f"Current Temp: {CurrentT}")
                        # self.ui.Temp_Label.update()
                        self.ui.Status.update()
                        if not self._is_running:
                            self.ui.Status.setText("Stopping...")
                            self.ui.Status.update()
                            break
                        SSComent = "T" + str(SetT)+"V"+str(volt)
                        
                        time.sleep(1)
                        pyautogui.keyDown("alt")
                        time.sleep(0.5)
                        if not self._is_running:
                            self.ui.Status.setText("Stopping...")
                            self.ui.Status.update()
                            break
                        pyautogui.keyDown("f")
                        time.sleep(0.5)
                        pyautogui.keyUp("alt")
                        pyautogui.keyUp("f")
                        time.sleep(1)
                        if not self._is_running:
                            self.ui.Status.setText("Stopping...")
                            self.ui.Status.update()
                            break
                        pyautogui.hotkey("S")
                        time.sleep(2)
                        app_control.type_in_application(self.BaseName)
                        app_control.type_in_application("-")
                        app_control.type_in_application(SSComent)
                        time.sleep(1)
                        if not self._is_running:
                            self.ui.Status.setText("Stopping...")
                            self.ui.Status.update()
                            break
                        pyautogui.hotkey("enter")
                        time.sleep(1)
                        pyautogui.hotkey("enter")
                        time.sleep(1)

            if self.LastTemp != 0:
                temp_probe.Set_Temp(self.LastTemp)
            # AVS_Done()
            
            if self.ui.Auto:
                time.sleep(1)
                pyautogui.press("ENTER")
                time.sleep(1)
            self.ui.Status.setText("Program END")
            self.ui.Status.update()
            print("Program Done")
            self._is_running = False
            
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

class MainWindow2(QMainWindow):
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
        self.Auto = False 
        self.text_fields = {
            "TempRes": QLineEdit(self),
            "Volt_List": QLineEdit(self),
            "Offset": QLineEdit(self),
            "Temp_List": QLineEdit(self), 
            "Folder": QLineEdit(self),
            "BaseName": QLineEdit(self),
            # "Temp_Wait": QLineEdit(self), # Used Once in the Temp loop
            "LastTemp": QLineEdit(self),
            "Accuracy": QLineEdit(self),
            "Frequency": QLineEdit(self),
            # "WaitingVoltage": QLineEdit(self),
            "AmpGain": QLineEdit(self),
            "WaitV": QLineEdit(self),
        }
        self.setGeometry(300, 300, 1500, 800)
        self.initUI()
        self.load_values()
        self.Form_Load()
    
    def initUI(self):
        
        self.setWindowTitle("AvaSpec UI")

        # Create main grid layout
        self.grid_layout = QGridLayout()

        # Create upper left and right boxes and the lower box
        self.upper_left_box = QVBoxLayout()
        self.upper_right_box = QVBoxLayout()
        self.lower_box = QVBoxLayout()

        # Populate the upper left box with some elements
        self.add_text(self.upper_left_box, "Volt_List"," Volt List")
        self.add_text(self.upper_left_box, "Temp_List", "Temperature list")
        self.add_text(self.upper_left_box, "LastTemp","Last Temperature")

        # Populate the upper right box with some elements
        Gen_Label = QLabel("Generator")
        Gen_Label.setFixedSize(200,20)#
        Gen_Label.setStyleSheet("QLabel{border:1px solid black}")
        self.upper_right_box.addWidget(Gen_Label)
        
        self.add_text(self.upper_right_box, "Offset", "Offset")
         # add_text(location , text_field_name, Label Name)
        self.add_text(self.upper_right_box, "WaitV", "Voltage wait time")
        self.add_text(self.upper_right_box, "Frequency", "Frequency")
        # self.add_text(self.upper_left_box, "WaitingVoltage","")
        self.add_text(self.upper_right_box, "AmpGain","Amp Gain")
        # Temp_Label = QLabel("Temperature Probe")
        # Temp_Label.setStyleSheet("QLabel{border:1px solid black}")
        # Temp_Label.setFixedSize(200,20)
        # self.upper_right_box.addWidget(Temp_Label)
        self.add_text(self.upper_right_box, "Accuracy", "Temperature Accuracy")
        self.add_text(self.upper_right_box, "TempRes", "Temperature Resolution")
        
        for field in self.text_fields.values():
            field.setFixedSize(200, 20)

        # Populate the lower box with some elements
        Folder_Label = QLabel("Folder")
        Folder_Label.setFixedSize(400,20)
        Folder_Field = self.text_fields["Folder"]
        Folder_Field.setFixedSize(300,20)
        self.lower_box.addWidget(Folder_Label)
        self.lower_box.addWidget(Folder_Field)

        BaseName_Label = QLabel("BaseName")
        BaseName_Label.setFixedSize(200,20)
        BaseName_Field = self.text_fields["BaseName"]
        BaseName_Field.setFixedSize(400,20)
        self.lower_box.addWidget(BaseName_Label)
        self.lower_box.addWidget(BaseName_Field)

        BaseName_Label.update()
        BaseName_Field.update()

        self.Status = QLabel('Status: Waiting', self)
        self.lower_box.addWidget(self.Status)
        self.Status.setStyleSheet("background-color: grey;")
        self.Status.setFixedSize(200, 100)  # Set the size of the label
        self.Status.setAlignment(Qt.AlignCenter)
        
        
        # self.Temp_Label = QLabel('Current Temp:', self)
        # self.lower_box.addWidget(self.Temp_Label)
        # self.Temp_Label.setStyleSheet("background-color: white;")
        # self.Temp_Label.setFixedSize(100, 50)  # Set the size of the label
    

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
        self.checkbox.stateChanged.connect(self.checkbox_state_FakeSignal)
        self.upper_left_box.addWidget(self.checkbox)
        
        # Fake Signal button
        self.checkbox2 = QCheckBox('AutoLaunch AvaSoft', self)
        self.checkbox2.stateChanged.connect(self.checkbox_state_Auto)
        self.upper_left_box.addWidget(self.checkbox2)

        # Create and set up the upper left widget
        self.upper_left_widget = QWidget()
        self.upper_left_widget.setLayout(self.upper_left_box)
        self.add_group_box_with_title(self.upper_left_widget, self.grid_layout, 
                                      'Inputs', 0, 0)

        # Create and set up the upper right widget
        self.upper_right_widget = QWidget()
        self.upper_right_widget.setLayout(self.upper_right_box)
        self.add_group_box_with_title(self.upper_right_widget, self.grid_layout, 
                                      'Configuration', 0, 1)

        # Create and set up the lower widget
        self.lower_widget = QWidget()
        self.lower_widget.setLayout(self.lower_box)
        self.add_group_box_with_title(self.lower_widget, self.grid_layout, 
                                      'Monitor', 1, 0, 1, 2)

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
            # self.main_program.exit()
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
        # QMessageBox.information(self,"Popup","The Program has Finished")
        self.show()
        self.isActiveWindow = True
        self.activateWindow()
        self.raise_()
        self.setFocus()
        self.Status.setText("Command finished")

    def closeEvent(self, event):
        self.save_values()
        super().closeEvent(event)

    def checkbox_state_FakeSignal(self, state):
        if state == 2:  # Checked
            print('Checkbox checked')
            self.Fake_Signal = True      
        else:  # Unchecked
            print('Checkbox unchecked')
            self.Fake_Signal = False 
            
    def checkbox_state_Auto(self, state):
        if state == 2:  # Checked
            print('Checkbox checked')
            self.Auto = True      
        else:  # Unchecked
            print('Checkbox unchecked')
            self.Auto = False 

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
        # if self.text_fields["Temp_Wait"].text() != "": 
        #     self.Temp_Wait = float(self.text_fields["Temp_Wait"].text())
        if self.text_fields["LastTemp"].text() != "": 
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

class QtdemoClass(QMainWindow, qtdemo.Ui_QtdemoClass):
    timer = QTimer() 
    SPECTR_LIST_COLUMN_COUNT = 5
    newdata = pyqtSignal(int, int)
    dstrStatus = pyqtSignal(int, int)

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.PreScanChk.hide()
        self.SetNirSensitivityRgrp.hide()
        self.setStatusBar(self.statusBar)
        self.tabWidget.setCurrentWidget(self.CommunicationTab)
        self.SpectrometerList.setSelectionMode(QAbstractItemView.SingleSelection)
        self.SpectrometerList.setColumnWidth(0,200)
        self.SpectrometerList.setColumnWidth(1,200)
        self.SpectrometerList.setColumnWidth(2,400)
        self.SpectrometerList.setColumnWidth(3,400)
        self.SpectrometerList.setColumnWidth(4,300)
        self.UpdateListBtn.setEnabled(False)
        self.ActivateBtn.setEnabled(False)
        self.DeactivateBtn.setEnabled(False)
        self.DigitalIoBtn.setEnabled(False)
        self.AnalogIoBtn.setEnabled(False)
        self.ShowEepromBtn.setEnabled(False)
        self.ReadEepromBtn.setEnabled(False)
        self.WriteEepromBtn.setEnabled(False)        
        self.StartMeasBtn.setEnabled(False)
        self.StopMeasBtn.setEnabled(False)
        self.ResetSpectrometerBtn.setEnabled(False)        
        self.ConnectUSBRBtn.setChecked(True)
        self.ConnectEthernetRBtn.setChecked(False)
        self.FixedNrRBtn.setChecked(True)
        self.ContinuousRBtn.setChecked(False)
        self.RepetitiveRBtn.setChecked(False)
        self.DstrStatusUpdateBtn.setEnabled(False)
        self.DstrProgBar.setRange(0, 1)
        self.DstrProgBar.setValue(0)
        self.DssEvent_Chk.setChecked(False)
        self.FoeEvent_Chk.setChecked(False)
        self.IErrorEvent_Chk.setChecked(False)
        self.SpectrometerList.clicked.connect(self.on_SpectrometerList_clicked)
#       self.OpenCommBtn.clicked.connect(self.on_OpenCommBtn_clicked)
#       for buttons, do not use explicit connect together with the on_ notation, or you will get
#       two signals instead of one!
        self.timer.timeout.connect(self.update_plot)
        self.timer.stop()
        self.newdata.connect(self.handle_newdata)
        self.dstrStatus.connect(self.handle_dstrstatus)
        self.DisableGraphChk.stateChanged.connect(self.on_DisableGraphChk_stateChanged)
        AVS_Done()
    def measure_cb(self, pparam1, pparam2):
        param1 = pparam1[0] # dereference the pointers
        param2 = pparam2[0]
        self.newdata.emit(param1, param2)

    def dstr_cb(self, pparam1, pparam2):
        param1 = pparam1[0] # dereference the pointers
        temp = ctypes.cast(ctypes.addressof(pparam2), ctypes.POINTER(ctypes.c_uint)) # change to correct type
        param2 = temp[0]
        self.dstrStatus.emit(param1, param2)

    @pyqtSlot()
#   if you leave out the @pyqtSlot() line, you will also get an extra signal!
#   so you might even get three!
    def on_OpenCommBtn_clicked(self):
        self.statusBar.showMessage('Open communication busy')
        la_Port = 0
        if (self.ConnectUSBRBtn.isChecked()):
            la_Port = 0
        if (self.ConnectEthernetRBtn.isChecked()): 
            la_Port = 256
        # if (self.ConnectBothRBtn.isChecked()):
        #     la_Port = -1      
        l_Ret = AVS_Init(la_Port)    
        if (l_Ret > 0):
            if (self.ConnectUSBRBtn.isChecked()):
                self.statusBar.showMessage("Initialized: USB (found devices: {0:d})".format(l_Ret))
            if (self.ConnectEthernetRBtn.isChecked()):
                self.statusBar.showMessage("Initialized: Ethernet (found devices: {0:d})".format(l_Ret))
            # if (self.ConnectBothRBtn.isChecked()):
            #     self.statusBar.showMessage("Initialized: Ethernet / USB (found devices: {0:d})".format(l_Ret))
            self.UpdateListBtn.setEnabled(True)
            self.on_UpdateListBtn_clicked()
        else:
            if (l_Ret == 0):
                self.statusBar.showMessage("No spectrometer found on network!")
            else:
                if (l_Ret == ERR_ETHCONN_REUSE):
                    # A list of spectrometers can still be provided by the DLL
                    self.statusBar.showMessage("Server error; another instance is running!")
                    self.on_UpdateListBtn_clicked()
                else:
                    self.statusBar.showMessage("Server error; open communication failed with AVS_Init() error: {0:d}".format(l_Ret))
            AVS_Done()
            # QMessageBox.critical(self,"Error","No devices were found!") 
        return

    @pyqtSlot()
    def on_CloseCommBtn_clicked(self):
        # First make sure that there is no measurement running, AVS_Done() must be called when 
        # there is no measurement running!
        if (globals.dev_handle != INVALID_AVS_HANDLE_VALUE):
            AVS_StopMeasure(globals.dev_handle)
            AVS_Deactivate(globals.dev_handle) 
            globals.dev_handle = INVALID_AVS_HANDLE_VALUE
        AVS_Done()
        self.DisconnectGui()  
        self.statusBar.showMessage('')
        self.SpectrometerList.clearContents()
        self.SpectrometerList.setRowCount(0)
        return

    @pyqtSlot()
    def on_UpdateListBtn_clicked(self):
        l_RequiredSize = 0
        if (len(self.SpectrometerList.selectedItems()) != 0):
            self.currentItem = self.SpectrometerList.currentItem()
            globals.mSelectedDevRow = self.currentItem.row()
        else:
            globals.mSelectedDevRow = 0
        self.SpectrometerList.clearContents()
        if (self.ConnectUSBRBtn.isChecked()):
            lUsbDevListSize = AVS_UpdateUSBDevices()
            l_pId = AvsIdentityType * lUsbDevListSize
            l_pId = AVS_GetList(lUsbDevListSize)
            self.SpectrometerList.setColumnCount(self.SPECTR_LIST_COLUMN_COUNT)
            self.SpectrometerList.setRowCount(lUsbDevListSize)
            x = 0
            while (x < lUsbDevListSize):
                self.SpectrometerList.setItem(x, 0, QTableWidgetItem(l_pId[x].SerialNumber.decode("utf-8")))
                if (l_pId[x].Status == b'\x00'):
                    self.SpectrometerList.setItem(x, 1, QTableWidgetItem("UNKNOWN"))
                if (l_pId[x].Status == b'\x01' ):
                    self.SpectrometerList.setItem(x, 1, QTableWidgetItem("USB_AVAILABLE"))
                if (l_pId[x].Status == b'\x02'):
                    self.SpectrometerList.setItem(x, 1, QTableWidgetItem("USB_IN_USE_BY_APPLICATION")) 
                if (l_pId[x].Status == b'\x03'):
                    self.SpectrometerList.setItem(x, 1, QTableWidgetItem("USB_IN_USE_BY_OTHER"))                                     
                x += 1 

        if (self.ConnectEthernetRBtn.isChecked()):  
            l_pEth = AVS_UpdateETHDevices(1)
            lEthListSize = len(l_pEth)
            l_pId = AvsIdentityType * lEthListSize
            l_pId = AVS_GetList(lEthListSize)
            self.SpectrometerList.setColumnCount(self.SPECTR_LIST_COLUMN_COUNT)
            self.SpectrometerList.setRowCount(lEthListSize)
            x = 0
            while (x < lEthListSize):
                self.SpectrometerList.setItem(x, 0, QTableWidgetItem(l_pId[x].SerialNumber.decode("utf-8")))
                if (l_pId[x].Status == b'\x04'):
                    self.SpectrometerList.setItem(x, 1, QTableWidgetItem("ETH_AVAILABLE"))  
                if (l_pId[x].Status == b'\x05'):
                    self.SpectrometerList.setItem(x, 1, QTableWidgetItem("ETH_IN_USE_BY_APPLICATION"))  
                if (l_pId[x].Status == b'\x06'):
                    self.SpectrometerList.setItem(x, 1, QTableWidgetItem("ETH_IN_USE_BY_OTHER"))                                                  
                if (l_pId[x].Status == b'\x07'):
                    self.SpectrometerList.setItem(x, 1, QTableWidgetItem("ETH_ALREADY_IN_USE_USB"))
                PortNumItem = ("{0:d}").format(l_pEth[x].port)    
                self.SpectrometerList.setItem(x, 2, QTableWidgetItem(PortNumItem))
                LocalIpItem = ("{0:d}.{1:d}.{2:d}.{3:d}").format(l_pEth[x].LocalIp & 0xff,
                                                                (l_pEth[x].LocalIp >> 8) & 0xff,
                                                                (l_pEth[x].LocalIp >> 16) & 0xff,
                                                                (l_pEth[x].LocalIp >> 24))
                self.SpectrometerList.setItem(x, 3, QTableWidgetItem(LocalIpItem))
                RemoteHostIpItem =  ("{0:d}.{1:d}.{2:d}.{3:d}").format(l_pEth[x].RemoteHostIp & 0xff,
                                                                      (l_pEth[x].RemoteHostIp >> 8) & 0xff,
                                                                      (l_pEth[x].RemoteHostIp >> 16) & 0xff,
                                                                      (l_pEth[x].RemoteHostIp >> 24))
                self.SpectrometerList.setItem(x, 4, QTableWidgetItem(RemoteHostIpItem))    
                x += 1 

        return 

    @pyqtSlot()
    def on_ActivateBtn_clicked(self):
        if (len(self.SpectrometerList.selectedItems()) == 0): 
            QMessageBox.critical(self, "Qt Demo", "Please select the Serial Number of the device to activate")
        else:
            l_Id = AvsIdentityType * 1
            l_Items = QListWidget()
            l_Items = self.SpectrometerList.selectedItems()
            l_Text = l_Items[0].text()
            l_Id.SerialNumber = l_Text.encode('utf-8')
            l_Id.UserFriendlyName = b"\x00"
            l_Id.Status = b"\x01"
            globals.dev_handle = AVS_Activate(l_Id)
            if (INVALID_AVS_HANDLE_VALUE == globals.dev_handle):
                QMessageBox.critical(self, "Qt Demo", "Error opening device {}".format(l_Text))
            else:
                m_Identity = l_Id
                globals.mSelectedDevRow = self.SpectrometerList.currentItem().row()
                self.on_UpdateListBtn_clicked()
                self.ConnectGui()
                self.on_ReadEepromBtn_clicked()
                dtype = 0
                dtype = AVS_GetDeviceType(globals.dev_handle)  
                if (dtype == 0):
                    self.DeviceTypeEdt.setText("Unknown")
                if (dtype == 1):
                    self.DeviceTypeEdt.setText("AS5216")
                if (dtype == 2):
                    self.DeviceTypeEdt.setText("ASMini")                                        
                if (dtype == 3):
                    self.DeviceTypeEdt.setText("AS7010")
                if (dtype == 4):
                    self.DeviceTypeEdt.setText("AS7007")                    
                self.DstrRBtn.setEnabled(dtype == 3)  # only available on AS7010
        return

    @pyqtSlot()
    def on_StartMeasBtn_clicked(self):
        ret = AVS_UseHighResAdc(globals.dev_handle, True)
        ret = AVS_EnableLogging(False)
        measconfig = MeasConfigType()
        measconfig.m_StartPixel = int(self.StartPixelEdt.text())
        measconfig.m_StopPixel = int(self.StopPixelEdt.text())
        measconfig.m_IntegrationTime = float(self.IntTimeEdt.text())
        l_NanoSec =  float(self.IntDelayEdt.text())
        measconfig.m_IntegrationDelay = int(6.0*(l_NanoSec+20.84)/125.0)
        measconfig.m_NrAverages = int(self.AvgEdt.text())
        measconfig.m_CorDynDark_m_Enable = self.DarkCorrChk.isChecked()
        measconfig.m_CorDynDark_m_ForgetPercentage = int(self.DarkCorrPercEdt.text())
        measconfig.m_Smoothing_m_SmoothPix = int(self.SmoothNrPixelsEdt.text())
        measconfig.m_Smoothing_m_SmoothModel = int(self.SmoothModelEdt.text())
        measconfig.m_SaturationDetection = int(self.SatDetEdt.text())
        if (self.SoftwareTriggerRBtn.isChecked()):
            measconfig.m_Trigger_m_Mode = 0
        if (self.HardwareTriggerRBtn.isChecked()):
            measconfig.m_Trigger_m_Mode = 1
        if (self.SingleScanTriggerRBtn.isChecked()):
            measconfig.m_Trigger_m_Mode = 2                
        measconfig.m_Trigger_m_Source =  self.SynchTriggerRBtn.isChecked()
        measconfig.m_Trigger_m_SourceType = self.LevelTriggerRBtn.isChecked()
        measconfig.m_Control_m_StrobeControl = int(self.FlashesPerScanEdt.text())
        l_NanoSec = float(self.LaserDelayEdt.text())        
        measconfig.m_Control_m_LaserDelay = int(6.0*l_NanoSec/125.0)
        l_NanoSec = float(self.LaserWidthEdt.text())
        measconfig.m_Control_m_LaserWidth = int(6.0*l_NanoSec/125.0)
        measconfig.m_Control_m_LaserWaveLength = float(self.LaserWavEdt.text())
        if (self.StoreToRamRBtn.isChecked() or self.DstrRBtn.isChecked()):
            measconfig.m_Control_m_StoreToRam = int(self.NrStoreToRamEdt.text())
        else:    
            measconfig.m_Control_m_StoreToRam = 0
        ret = AVS_PrepareMeasure(globals.dev_handle, measconfig)
        if (globals.DeviceData.m_Detector_m_SensorType == SENS_TCD1304):
            AVS_SetPrescanMode(globals.dev_handle, self.PreScanChk.isChecked())
        if ((globals.DeviceData.m_Detector_m_SensorType == SENS_HAMS9201) or 
            (globals.DeviceData.m_Detector_m_SensorType == SENS_SU256LSB) or
            (globals.DeviceData.m_Detector_m_SensorType == SENS_SU512LDB)):
            AVS_SetSensitivityMode(globals.dev_handle, self.HighSensitivityRBtn.isChecked())
        if (self.FixedNrRBtn.isChecked()):
            l_NrOfScans = int(self.NrMeasEdt.text())
        if (self.ContinuousRBtn.isChecked()):
            l_NrOfScans = -1
        if (self.RepetitiveRBtn.isChecked()):
             l_NrOfScans = int(self.NrMeasEdt.text())
        if (self.StoreToRamRBtn.isChecked()):
            l_NrOfScans = 1
        if (self.DstrRBtn.isChecked()):
            l_NrOfScans = -2
            dynstr_cb = AVS_DstrCallbackFunc(self.dstr_cb)
            l_Res = AVS_SetDstrStatusCallback(globals.dev_handle, dynstr_cb)
        if (self.StartMeasBtn.isEnabled()):
            globals.m_DateTime_start = QDateTime.currentDateTime()
            globals.m_SummatedTimeStamps = 0.0
            globals.m_Measurements = 0
            globals.m_Failures = 0
            self.TimeSinceStartEdt.setText("{0:d}".format(0))
            self.NrScansEdt.setText("{0:d}".format(0))
            self.NrFailuresEdt.setText("{0:d}".format(0))
        self.StartMeasBtn.setEnabled(False) 
        self.timer.start(200)   
        globals.startpixel = measconfig.m_StartPixel
        globals.stoppixel = measconfig.m_StopPixel
        if (self.RepetitiveRBtn.isChecked()):
            lmeas = 0
            while (self.StartMeasBtn.isEnabled() == False):
                avs_cb = AVS_MeasureCallbackFunc(self.measure_cb)
                l_Res = AVS_MeasureCallback(globals.dev_handle, avs_cb, 1)
                while (globals.m_Measurements - lmeas) < 1: 
                    time.sleep(0.001)
                    qApp.processEvents()
                lmeas += 1
        else:    
            avs_cb = AVS_MeasureCallbackFunc(self.measure_cb)
            l_Res = AVS_MeasureCallback(globals.dev_handle, avs_cb, l_NrOfScans)
            if (0 != l_Res):
                self.statusBar.showMessage("AVS_MeasureCallback failed, error: {0:d}".format(l_Res))    
            else:
                globals.mDstrRecvCount = 0
                self.DstrStatusRecvCountEdt.setText("{0:d}".format(globals.mDstrRecvCount))
                if (self.DstrRBtn.isChecked() == False):
                    # Reset all fields that have nothing to do with DSTR
                    self.DstrTotalScansEdt.setText("")
                    self.DstrUsedScansEdt.setText("")
                    self.DstrFlagsEdt.setText("")
                    self.DstrProgBar.setValue(0)
                    self.DssEvent_Chk.setChecked(False)
                    self.FoeEvent_Chk.setChecked(False)
                    self.IErrorEvent_Chk.setChecked(False)
                    self.statusBar.showMessage("Meas.Status: pending")
                if (self.FixedNrRBtn.isChecked()):
                    while globals.m_Measurements <= l_NrOfScans:
                        time.sleep(0.001)
                        qApp.processEvents()
                else:        
                    if (self.ContinuousRBtn.isChecked() or
                        self.StoreToRamRBtn.isChecked() or
                        self.DstrRBtn.isChecked()):
                        while True: 
                            time.sleep(0.001)
                            qApp.processEvents()
        return

    @pyqtSlot()
    def on_StopMeasBtn_clicked(self): 
        ret = AVS_StopMeasure(globals.dev_handle)
        self.StartMeasBtn.setEnabled(True)
        self.timer.stop()
        return

    @pyqtSlot()
    def update_plot(self):
        if (self.DisableGraphChk.isChecked() == False):
            self.plot.update_plot()
        if (globals.m_Measurements == int(self.NrMeasEdt.text())):
            self.StartMeasBtn.setEnabled(True)    
        return         

    @pyqtSlot(int, int)
    def handle_newdata(self, ldev_handle, lerror):
        if (lerror >= 0):
            if ((ldev_handle == globals.dev_handle) and (globals.pixels > 0)):
                if (lerror == 0): # normal measurements
                    self.statusBar.showMessage("Meas.Status: success")
                    timestamp = 0
                    globals.m_Measurements += 1
                    timestamp, globals.spectraldata = AVS_GetScopeData(globals.dev_handle)
                    globals.saturated = AVS_GetSaturatedPixels(globals.dev_handle)
                    SpectrumIsSatured = False
                    j = 0
                    while j < (globals.stoppixel - globals.startpixel):
                        SpectrumIsSatured = SpectrumIsSatured or globals.saturated[j]
                        j += 1
                        self.SaturatedChk.setChecked(SpectrumIsSatured)
                    # self.plot.update_plot()
                    l_Dif = timestamp - globals.m_PreviousTimeStamp  # timestamps in 10 us ticks
                    globals.m_PreviousTimeStamp = timestamp
                    if (globals.m_Measurements > 1):
                        globals.m_SummatedTimeStamps += l_Dif
                        self.LastScanEdt.setText("{0:.3f}".format(l_Dif/100.0))  # in millisec
                        timeperscan = float(globals.m_SummatedTimeStamps) / float(100.0 * (globals.m_Measurements - 1))
                        self.TimePerScanEdt.setText("{0:.3f}".format(timeperscan))
                    else:
                        self.LastScanEdt.setText("")
                        self.TimePerScanEdt.setText("")
                    l_Seconds = globals.m_DateTime_start.secsTo(QDateTime.currentDateTime())
                    self.TimeSinceStartEdt.setText("{0:d}".format(l_Seconds))
                    self.NrScansEdt.setText("{0:d}".format(globals.m_Measurements))
                    if (self.FixedNrRBtn.isChecked()):
                       self.StartMeasBtn.setEnabled(int(self.NrMeasEdt.text()) == globals.m_Measurements) 
                else: # StoreToRam measurements
                    l_AvgScantimeRAM = 0.0
                    self.statusBar.showMessage("Meas.Status: Reading RAM")
                    j = 0
                    while j < lerror:
                        timestamp, globals.spectraldata = AVS_GetScopeData(globals.dev_handle)
                        # self.plot.update_plot()
                        l_Dif = timestamp - globals.m_PreviousTimeStamp  # timestamps in 10 us ticks
                        globals.m_PreviousTimeStamp = timestamp
                        if (j > 1):
                            globals.m_SummatedTimeStamps += l_Dif
                            self.LastScanEdt.setText("{0:.3f}".format(l_Dif/100.0))  # in millisec
                            timeperscan = float(globals.m_SummatedTimeStamps) / float(100.0 * (j - 1))
                            self.TimePerScanEdt.setText("{0:.3f}".format(timeperscan))
                        else:
                            self.LastScanEdt.setText("")
                            self.TimePerScanEdt.setText("")
                        l_Seconds = globals.m_DateTime_start.secsTo(QDateTime.currentDateTime())
                        self.TimeSinceStartEdt.setText("{0:d}".format(l_Seconds))
                        self.NrScansEdt.setText("{0:d}".format(j+1))
                        j += 1
                    self.statusBar.showMessage("Meas.Status: Finished Reading RAM")    
                    self.StartMeasBtn.setEnabled(True)    
        else:
            self.statusBar.showMessage("Meas.Status: failed. {0:d})".format(lerror))
            globals.m_Failures += 1
        self.NrFailuresEdt.setText("{0:d}".format(globals.m_Failures))    
        return

    @pyqtSlot(int, int)
    def handle_dstrstatus(self, ldev_handle, lstatus):
        if (ldev_handle == globals.dev_handle): 
            globals.mDstrRecvCount += 1
            self.on_DstrStatusUpdateBtn_clicked()
        if (lstatus > 0):
            self.StartMeasBtn.setEnabled(True)
        return

    @pyqtSlot()
    def on_DstrStatusUpdateBtn_clicked(self):
        l_DstrStatus = DstrStatusType()
        l_DstrStatus = AVS_GetDstrStatus(globals.dev_handle)
        if (self.DstrRBtn.isChecked() == True):
            self.DstrStatusRecvCountEdt.setText("{0:d}".format(globals.mDstrRecvCount))
            self.DstrTotalScansEdt.setText("{0:d}".format(l_DstrStatus.m_TotalScans))
            self.DstrUsedScansEdt.setText("{0:d}".format(l_DstrStatus.m_UsedScans))
            self.DstrFlagsEdt.setText("{0:08b}".format(l_DstrStatus.m_Flags))
            self.DssEvent_Chk.setChecked(l_DstrStatus.m_Flags & DSTR_STATUS_DSS_MASK)
            self.FoeEvent_Chk.setChecked(l_DstrStatus.m_Flags & DSTR_STATUS_FOE_MASK)
            self.IErrorEvent_Chk.setChecked(l_DstrStatus.m_Flags & DSTR_STATUS_IERR_MASK) 
            if (l_DstrStatus.m_TotalScans > 0):
                self.DstrProgBar.setRange(0, l_DstrStatus.m_TotalScans)
                self.DstrProgBar.setValue(l_DstrStatus.m_UsedScans)      
        return    

    @pyqtSlot()
    def on_ReadEepromBtn_clicked(self):
        l_DeviceData = DeviceConfigType()
        l_DeviceData = AVS_GetParameter(globals.dev_handle, 63484)
        # show measurement settings
        self.StartPixelEdt.setText("{0:d}".format(l_DeviceData.m_StandAlone_m_Meas_m_StartPixel))
        self.StopPixelEdt.setText("{0:d}".format(l_DeviceData.m_StandAlone_m_Meas_m_StopPixel))
        self.IntTimeEdt.setText("{0:.3f}".format(l_DeviceData.m_StandAlone_m_Meas_m_IntegrationTime))
        l_FPGAClkCycles = l_DeviceData.m_StandAlone_m_Meas_m_IntegrationDelay
        l_NanoSec = 125.0*(l_FPGAClkCycles-1.0)/6.0
        self.IntDelayEdt.setText("{0:.0f}".format(l_NanoSec))
        self.AvgEdt.setText("{0:d}".format(l_DeviceData.m_StandAlone_m_Meas_m_NrAverages))
        self.SatDetEdt.setText("{0:d}".format(l_DeviceData.m_StandAlone_m_Meas_m_SaturationDetection))
        self.SoftwareTriggerRBtn.setChecked(l_DeviceData.m_StandAlone_m_Meas_m_Trigger_m_Mode == 0)
        self.HardwareTriggerRBtn.setChecked(l_DeviceData.m_StandAlone_m_Meas_m_Trigger_m_Mode == 1)
        self.SingleScanTriggerRBtn.setChecked(l_DeviceData.m_StandAlone_m_Meas_m_Trigger_m_Mode == 2)
        self.ExternalTriggerRbtn.setChecked(l_DeviceData.m_StandAlone_m_Meas_m_Trigger_m_Source == 0)
        self.SynchTriggerRBtn.setChecked(l_DeviceData.m_StandAlone_m_Meas_m_Trigger_m_Source == 1)
        self.EdgeTriggerRBtn.setChecked(l_DeviceData.m_StandAlone_m_Meas_m_Trigger_m_SourceType == 0)
        self.LevelTriggerRBtn.setChecked(l_DeviceData.m_StandAlone_m_Meas_m_Trigger_m_SourceType == 1)
        self.DarkCorrChk.setChecked(l_DeviceData.m_StandAlone_m_Meas_m_CorDynDark_m_Enable == 1)
        self.DarkCorrPercEdt.setText("{0:d}".format(l_DeviceData.m_StandAlone_m_Meas_m_CorDynDark_m_ForgetPercentage))
        self.SmoothModelEdt.setText("{0:d}".format(l_DeviceData.m_StandAlone_m_Meas_m_Smoothing_m_SmoothModel))
        self.SmoothNrPixelsEdt.setText("{0:d}".format(l_DeviceData.m_StandAlone_m_Meas_m_Smoothing_m_SmoothPix))
        self.FlashesPerScanEdt.setText("{0:d}".format(l_DeviceData.m_StandAlone_m_Meas_m_Control_m_StrobeControl))
        l_FPGAClkCycles = l_DeviceData.m_StandAlone_m_Meas_m_Control_m_LaserDelay
        l_NanoSec = 125.0*(l_FPGAClkCycles)/6.0
        self.LaserDelayEdt.setText("{0:.0f}".format(l_NanoSec))
        l_FPGAClkCycles = l_DeviceData.m_StandAlone_m_Meas_m_Control_m_LaserWidth
        l_NanoSec = 125.0*(l_FPGAClkCycles)/6.0
        self.LaserWidthEdt.setText("{0:.0f}".format(l_NanoSec))
        self.LaserWavEdt.setText("{0:.3f}".format(l_DeviceData.m_StandAlone_m_Meas_m_Control_m_LaserWaveLength))
        self.NrStoreToRamEdt.setText("{0:d}".format(l_DeviceData.m_StandAlone_m_Meas_m_Control_m_StoreToRam))
        self.NrMeasEdt.setText("{0:d}".format(l_DeviceData.m_StandAlone_m_Nmsr))                
        return

    @pyqtSlot()
    def on_WriteEepromBtn_clicked(self): 
        l_DeviceData = DeviceConfigType()
        l_DeviceData = AVS_GetParameter(globals.dev_handle, 63484)
        l_DeviceData.m_StandAlone_m_Meas_m_StartPixel = int(self.StartPixelEdt.text())
        l_DeviceData.m_StandAlone_m_Meas_m_StopPixel =  int(self.StopPixelEdt.text())
        l_DeviceData.m_StandAlone_m_Meas_m_IntegrationTime = float(self.IntTimeEdt.text())
        l_NanoSec = float(self.IntDelayEdt.text())
        l_DeviceData.m_StandAlone_m_Meas_m_IntegrationDelay = int(6.0*(l_NanoSec+20.84)/125.0)
        l_DeviceData.m_StandAlone_m_Meas_m_NrAverages = int(self.AvgEdt.text())
        if (self.SoftwareTriggerRBtn.isChecked()):
            l_DeviceData.m_StandAlone_m_Meas_m_Trigger_m_Mode = 0
        if (self.HardwareTriggerRBtn.isChecked()):
            l_DeviceData.m_StandAlone_m_Meas_m_Trigger_m_Mode = 1
        if (self.SingleScanTriggerRBtn.isChecked()):
            l_DeviceData.m_StandAlone_m_Meas_m_Trigger_m_Mode = 2
        l_DeviceData.m_StandAlone_m_Meas_m_Trigger_m_Source = self.SynchTriggerRBtn.isChecked()
        l_DeviceData.m_StandAlone_m_Meas_m_Trigger_m_SourceType = self.LevelTriggerRBtn.isChecked()
        l_DeviceData.m_StandAlone_m_Meas_m_SaturationDetection = int(self.SatDetEdt.text())
        l_DeviceData.m_StandAlone_m_Meas_m_CorDynDark_m_Enable = self.DarkCorrChk.isChecked()
        l_DeviceData.m_StandAlone_m_Meas_m_CorDynDark_m_ForgetPercentage = int(self.DarkCorrPercEdt.text())
        l_DeviceData.m_StandAlone_m_Meas_m_Smoothing_m_SmoothPix = int(self.SmoothNrPixelsEdt.text())
        l_DeviceData.m_StandAlone_m_Meas_m_Smoothing_m_SmoothModel = int(self.SmoothModelEdt.text())
        l_DeviceData.m_StandAlone_m_Meas_m_Control_m_StrobeControl = int(self.FlashesPerScanEdt.text())
        l_NanoSec = float(self.LaserDelayEdt.text())
        l_DeviceData.m_StandAlone_m_Meas_m_Control_m_LaserDelay = int(6.0*l_NanoSec/125.0)
        l_NanoSec = float(self.LaserWidthEdt.text())
        l_DeviceData.m_StandAlone_m_Meas_m_Control_m_LaserWidth = int(6.0*l_NanoSec/125.0)
        l_DeviceData.m_StandAlone_m_Meas_m_Control_m_LaserWaveLength = float(self.LaserWavEdt.text())
        l_DeviceData.m_StandAlone_m_Meas_m_Control_m_StoreToRam = int(self.NrStoreToRamEdt.text())
        l_DeviceData.m_StandAlone_m_Nmsr = int(self.NrMeasEdt.text())
        # write measurement parameters
        # debug = ctypes.sizeof(l_DeviceData)
        l_Ret = AVS_SetParameter(globals.dev_handle, l_DeviceData)
        if (0 != l_Ret):
            QMessageBox.critical(self, "Qt Demo", "AVS_SetParameter failed, code {0:d}".format(l_Ret))
        return        

    @pyqtSlot()
    def on_SpectrometerList_clicked(self):
        if (len(self.SpectrometerList.selectedItems()) != 0):
            self.UpdateButtons()
        return      

    def ConnectGui(self):
        versions = AVS_GetVersionInfo(globals.dev_handle)
        self.FPGAVerEdt.setText("{}".format(str(versions[0],"utf-8")))
        self.FirmwareVerEdt.setText("{}".format(str(versions[1],"utf-8")))
        self.DLLVerEdt.setText("{}".format(str(versions[2],"utf-8")))
        globals.DeviceData = DeviceConfigType()
        globals.DeviceData = AVS_GetParameter(globals.dev_handle, 63484)
        lDetectorName = AVS_GetDetectorName(globals.dev_handle, globals.DeviceData.m_Detector_m_SensorType)
        a_DetectorName = str(lDetectorName,"utf-8").split("\x00") 
        self.DetectorEdt.setText("{}".format(a_DetectorName[0]))
        if (globals.DeviceData.m_Detector_m_SensorType == SENS_HAMS9201):
            self.SetNirSensitivityRgrp.show()
            self.LowNoiseRBtn.setChecked(True)  # LowNoise default for HAMS9201
            self.HighSensitivityRBtn.setChecked(False)
            AVS_SetSensitivityMode(globals.dev_handle, 0)
        if (globals.DeviceData.m_Detector_m_SensorType == SENS_TCD1304):    
            self.PreScanChk.show()    
            self.PreScanChk.setCheckState(Qt.Checked)
            l_Res = AVS_SetPrescanMode(globals.dev_handle, self.PreScanChk.isChecked()) 
        if (globals.DeviceData.m_Detector_m_SensorType == SENS_SU256LSB):
            self.SetNirSensitivityRgrp.show()
            self.LowNoiseRBtn.setChecked(False)
            self.HighSensitivityRBtn.setChecked(True)  # High Sensitive default for SU256LSB
            l_Res = AVS_SetSensitivityMode(globals.dev_handle, 1)
        if (globals.DeviceData.m_Detector_m_SensorType == SENS_SU512LDB):
            self.SetNirSensitivityRgrp.show()
            self.LowNoiseRBtn.setChecked(False)
            self.HighSensitivityRBtn.setChecked(True)  # High Sensitive default for SU512LDB
            l_Res = AVS_SetSensitivityMode(globals.dev_handle, 1) 
        if (globals.DeviceData.m_Detector_m_SensorType == SENS_HAMG9208_512):
            self.SetNirSensitivityRgrp.show()
            self.LowNoiseRBtn.setChecked(True)  # low noise default
            self.HighSensitivityRBtn.setChecked(False)
            l_Res = AVS_SetSensitivityMode(globals.dev_handle, 0) 
        globals.pixels = globals.DeviceData.m_Detector_m_NrPixels
        self.NrPixelsEdt.setText("{0:d}".format(globals.pixels))
        globals.startpixel = globals.DeviceData.m_StandAlone_m_Meas_m_StartPixel
        globals.stoppixel = globals.DeviceData.m_StandAlone_m_Meas_m_StopPixel
        globals.wavelength = AVS_GetLambda(globals.dev_handle)
        return

    def DisconnectGui(self):
        self.DetectorEdt.clear()
        self.NrPixelsEdt.clear()
        self.FPGAVerEdt.clear()
        self.FirmwareVerEdt.clear()
        self.DLLVerEdt.clear()
        self.DeviceTypeEdt.clear()
        self.ActivateBtn.setEnabled(False)
        self.DeactivateBtn.setEnabled(False)
        self.DigitalIoBtn.setEnabled(False)
        self.AnalogIoBtn.setEnabled(False)
        self.ShowEepromBtn.setEnabled(False)
        self.ReadEepromBtn.setEnabled(False)
        self.WriteEepromBtn.setEnabled(False)
        self.StartMeasBtn.setEnabled(False)
        self.DstrStatusUpdateBtn.setEnabled(False)
        self.StopMeasBtn.setEnabled(False)
        self.ResetSpectrometerBtn.setEnabled(False)
        return

    def UpdateButtons(self):
        s = self.SpectrometerList.item(self.SpectrometerList.currentRow(), 1).text()
        self.ActivateBtn.setEnabled(s == "USB_AVAILABLE" or s == "ETH_AVAILABLE")
        self.DeactivateBtn.setEnabled(s == "USB_IN_USE_BY_APPLICATION" or s == "ETH_IN_USE_BY_APPLICATION")
        self.DigitalIoBtn.setEnabled(s == "USB_IN_USE_BY_APPLICATION" or s == "ETH_IN_USE_BY_APPLICATION")
        self.AnalogIoBtn.setEnabled(s == "USB_IN_USE_BY_APPLICATION" or s == "ETH_IN_USE_BY_APPLICATION")
        self.ShowEepromBtn.setEnabled(s == "USB_IN_USE_BY_APPLICATION" or s == "ETH_IN_USE_BY_APPLICATION")
        self.ReadEepromBtn.setEnabled(s == "USB_IN_USE_BY_APPLICATION" or s == "ETH_IN_USE_BY_APPLICATION")
        self.WriteEepromBtn.setEnabled(s == "USB_IN_USE_BY_APPLICATION" or s == "ETH_IN_USE_BY_APPLICATION")       
        self.StartMeasBtn.setEnabled(s == "USB_IN_USE_BY_APPLICATION" or s == "ETH_IN_USE_BY_APPLICATION")
        self.DstrStatusUpdateBtn.setEnabled(s == "USB_IN_USE_BY_APPLICATION" or s == "ETH_IN_USE_BY_APPLICATION")
        self.StopMeasBtn.setEnabled(s == "USB_IN_USE_BY_APPLICATION" or s == "ETH_IN_USE_BY_APPLICATION")
        self.ResetSpectrometerBtn.setEnabled(s == "USB_IN_USE_BY_APPLICATION" or s == "ETH_IN_USE_BY_APPLICATION")
        return 

    @pyqtSlot()
    def on_DeactivateBtn_clicked(self):
        ret = AVS_Deactivate(globals.dev_handle)
        globals.dev_handle = INVALID_AVS_HANDLE_VALUE
        self.on_UpdateListBtn_clicked()
        self.DisconnectGui()
        return

    @pyqtSlot()
    def on_AnalogIoBtn_clicked(self):
        w2 = analog_io_demo.AnalogIoDialog(self)
        w2.show()
        return

    @pyqtSlot()
    def on_DigitalIoBtn_clicked(self):
        w3 = digital_io_demo.DigitalIoDialog(self)
        w3.show()
        return

    @pyqtSlot()
    def on_ShowEepromBtn_clicked(self):
        w4 = eeprom_demo.EepromDialog(self)
        w4.show()        
        return

    @pyqtSlot()
    def on_ResetSpectrometerBtn_clicked(self):
        l_Ret = AVS_ResetDevice( globals.dev_handle)
        if (0 != l_Ret):
            QMessageBox.critical(self, "Qt Demo", "AVS_ResetDevice failed, code {0:d}".format(l_Ret))
        else:
            self.on_CloseCommBtn_clicked()    
        return

    @pyqtSlot()
    def on_DisableGraphChk_stateChanged(self):
        globals.m_GraphicsDisabled = self.DisableGraphChk.isChecked()
        return     # def main():
#     """ Main function to run the application """
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     sys.exit(app.exec_())

# if __name__ == '__main__':
#     main()

class TabbedApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tabbed PyQt5 Application")
        self.resize(1500,800)
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.tab1 = QtdemoClass()
        self.tab2 = MainWindow2()

        self.tabs.addTab(self.tab1, "Tab 1")
        self.tabs.addTab(self.tab2, "Tab 2")
    def resizeEvent(self, event):
        super().resizeEvent(event)
        scale_factor = self.width() / 1500  # Base scale factor on the initial width
        self.setStyleSheet(f"""
            QWidget {{
                font-size: {20 * scale_factor}px;
               
                min-width: {200 * scale_factor}px;
                min-height: {20 * scale_factor}px;
            }}
            QPushButton {{
                font-size: {10 * scale_factor}px;
          
                min-width: {200 * scale_factor}px;
                min-height: {20 * scale_factor}px;
            }}
            QLabel {{
                font-size: {10 * scale_factor}px;
                min-width: {200 * scale_factor}px;
                min-height: {20 * scale_factor}px;
                }}
            QCheckBox{{
                font-size: {10 * scale_factor}px;
                min-width: {200 * scale_factor}px;
                min-height: {20 * scale_factor}px;
                }}
            QLineEdit{{
                font-size: {10 * scale_factor}px;
                min-width: {200 * scale_factor}px;
                min-height: {20 * scale_factor}px;
                }}
        """)
def main():
    app = QApplication(sys.argv)
    # app.setStyleSheet("""QWidget{font-size:25px; },             
    #                   QPushButton{min-width: 100px; min-height: 100px;},
    #                   QLabel{font-size: 18px;border: 1px solid black;min-height: 60px;,min-width: 100px;}""")#padding: 10px; margin: 5px;
    
    app.lastWindowClosed.connect(app.quit)
    main_app = TabbedApp()
    main_app.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()