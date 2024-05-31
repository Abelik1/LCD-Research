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
import globals
import form1
from AvaData import *
# from avaspec import *
from Generator import *
from Temp_Probe import *

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
                self.ui.Temp_Label.setText(f"Current Temp: {CurrentT}")
                self.ui.Temp_Label.update()
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
                        self.ui.Temp_Label.setText(f"Current Temp: {CurrentT}")
                        self.ui.Temp_Label.update()
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
        self.add_text(self.upper_left_box, "Volt_List"," Volt List")
        self.add_text(self.upper_left_box, "Temp_List", "Temperature list")
        self.add_text(self.upper_left_box, "LastTemp","Last Temperature")

        # Populate the upper right box with some elements
        Gen_Label = QLabel("Generator")
        Gen_Label.setFixedSize(100,20)
        self.lower_box.addWidget(Gen_Label)
        self.add_text(self.upper_right_box, "Offset", "Offset")
         # add_text(location , text_field_name, Label Name)
        self.add_text(self.upper_right_box, "WaitV", "Voltage wait time")
        self.add_text(self.upper_right_box, "Frequency", "Frequency")
        # self.add_text(self.upper_left_box, "WaitingVoltage","")
        self.add_text(self.upper_right_box, "AmpGain","Amp Gain")
        Temp_Label = QLabel("Temperature Probe")
        Temp_Label.setFixedSize(150,20)
        self.lower_box.addWidget(Temp_Label)
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
        
        
        self.Temp_Label = QLabel('Current Temp:', self)
        self.lower_box.addWidget(self.Temp_Label)
        self.Temp_Label.setStyleSheet("background-color: white;")
        self.Temp_Label.setFixedSize(100, 50)  # Set the size of the label
    

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


class MainWindow1(QMainWindow, form1.Ui_MainWindow):
    timer = QTimer()
    newdata = pyqtSignal(int, int)

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.IntTimeEdt.setText("{:3.1f}".format(5.0))
        self.NumAvgEdt.setText("{0:d}".format(1))
        self.NumMeasEdt.setText("{0:d}".format(1))
        self.StartMeasBtn.setEnabled(False)
#       self.OpenCommBtn.clicked.connect(self.on_OpenCommBtn_clicked)
#       For the buttons, do not use explicit connect together with the on_ notation, 
#       or you will get two signals instead of one!
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(200)
        self.newdata.connect(self.handle_newdata)

    def measure_cb(self, pparam1, pparam2):
        param1 = pparam1[0] # dereference the pointers
        param2 = pparam2[0]
        self.newdata.emit(param1, param2) 

    @pyqtSlot()
#   if you leave out the @pyqtSlot() line, you will also get an extra signal!
#   so you might even get three!
    def on_OpenCommBtn_clicked(self):
        ret = AVS_Init(0)    
        # QMessageBox.information(self,"Info","AVS_Init returned:  {0:d}".format(ret))
        ret = AVS_GetNrOfDevices()
        # QMessageBox.information(self,"Info","AVS_GetNrOfDevices returned:  {0:d}".format(ret))
        if (ret > 0):
            mylist = AvsIdentityType * 1
            mylist = AVS_GetList(1)
            serienummer = str(mylist[0].SerialNumber.decode("utf-8"))
            QMessageBox.information(self,"Info","Found Serialnumber: " + serienummer)
            globals.dev_handle = AVS_Activate(mylist[0])
            # QMessageBox.information(self,"Info","AVS_Activate returned:  {0:d}".format(globals.dev_handle))
            devcon = DeviceConfigType()
            devcon = AVS_GetParameter(globals.dev_handle, 63484)
            globals.pixels = devcon.m_Detector_m_NrPixels
            globals.wavelength = AVS_GetLambda(globals.dev_handle)
            self.StartMeasBtn.setEnabled(True)
        else:
            QMessageBox.critical(self,"Error","No devices were found!") 
        return

    @pyqtSlot()
    def on_CloseCommBtn_clicked(self):
        # nothing for now
        return

    @pyqtSlot()
    def on_StartMeasBtn_clicked(self):
        self.StartMeasBtn.setEnabled(False)
        ret = AVS_UseHighResAdc(globals.dev_handle, True)
        measconfig = MeasConfigType()
        measconfig.m_StartPixel = 0
        measconfig.m_StopPixel = globals.pixels - 1
        measconfig.m_IntegrationTime = float(self.IntTimeEdt.text())
        measconfig.m_IntegrationDelay = 0
        measconfig.m_NrAverages = int(self.NumAvgEdt.text())
        measconfig.m_CorDynDark_m_Enable = 0  # nesting of types does NOT work!!
        measconfig.m_CorDynDark_m_ForgetPercentage = 0
        measconfig.m_Smoothing_m_SmoothPix = 0
        measconfig.m_Smoothing_m_SmoothModel = 0
        measconfig.m_SaturationDetection = 0
        measconfig.m_Trigger_m_Mode = 0
        measconfig.m_Trigger_m_Source = 0
        measconfig.m_Trigger_m_SourceType = 0
        measconfig.m_Control_m_StrobeControl = 0
        measconfig.m_Control_m_LaserDelay = 0
        measconfig.m_Control_m_LaserWidth = 0
        measconfig.m_Control_m_LaserWaveLength = 0.0
        measconfig.m_Control_m_StoreToRam = 0
        ret = AVS_PrepareMeasure(globals.dev_handle, measconfig)
        nummeas = int(self.NumMeasEdt.text())
        globals.NrScanned = 0
        avs_cb = AVS_MeasureCallbackFunc(self.measure_cb)
        AVS_MeasureCallback(globals.dev_handle, avs_cb, nummeas)
        while nummeas != globals.NrScanned: # wait until data has arrived
            time.sleep(0.001)
            qApp.processEvents()
        self.StartMeasBtn.setEnabled(True)      
        return

    @pyqtSlot()
    def on_StopMeasBtn_clicked(self):
        ret = AVS_StopMeasure(globals.dev_handle)
        self.StartMeasBtn.setEnabled(True)
        return

    @pyqtSlot()
    def update_plot(self):
        self.plot.update_plot()
        if (globals.NrScanned == int(self.NumMeasEdt.text())):
            self.StartMeasBtn.setEnabled(True)    
        return        

    @pyqtSlot(int, int)
    def handle_newdata(self, lparam1, lparam2):
        #print(lparam1)
        #print(lparam2)
        timestamp = 0
        ret = AVS_GetScopeData(globals.dev_handle)
        timestamp = ret[0]
        globals.NrScanned += 1  
        globals.spectraldata = ret[1]
        # QMessageBox.information(self,"Info","Received data")
        return
# def main():
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

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.tab1 = MainWindow1()
        self.tab2 = MainWindow2()

        self.tabs.addTab(self.tab1, "Tab 1")
        self.tabs.addTab(self.tab2, "Tab 2")

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet("QWidget{font-size:20px}")
    app.lastWindowClosed.connect(app.quit)
    main_app = TabbedApp()
    main_app.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()