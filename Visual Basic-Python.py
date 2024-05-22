# % = integer
# Single precision floating = As single
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QLineEdit, QCheckBox, QMessageBox
from PyQt5.QtCore import QTimer
import ctypes
import time
import re

# Import the AvaSpec functions (assuming the provided AvaSpec code is in a module named avaspec)
import avaspec

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

        self.Gen_id = 0
        self.dev_Osc = ""
        self.Command = ""
        self.param = ""
        self.Out_File = ""
        self.Out_Data = ""
        self.Volt_List = ""
        self.Temp_List = ""
        self.ReadBuffer = ""
        self.Frequency = [0] * 300
        self.Voltage = [0] * 300
        self.Temperature = [0] * 5000
        self.Freq = 0.0
        self.Amplitude = 0.0
        self.Offset = 0.0
        self.AmpGain = 0.0
        self.AvPer = 0.0
        self.VScal = 0.0
        self.VScalMax = 0.0
        self.Vmax = 0.0
        self.Temp_Wait = 0.0
        self.LastTemp = 0.0
        self.WaitV = 0.0
        self.WaitingVoltage = 0.0
        self.Accuracy = 0.0
        self.CurrentT = 0.0
        self.SetT = 0.0
        self.Num_Volt = 0
        self.Num_Temp = 0
        self.TemRes = 0
        self.Fast = False
        self.AST = False
        self.ASV = False
        self.Expire = False
        self.DCmode = False

    def initUI(self):
        self.setWindowTitle("AvaSpec Control")

        self.label = QLabel("Status: Idle", self)
        self.button1 = QPushButton("Start", self)
        self.button2 = QPushButton("Stop", self)
        self.text15 = QLineEdit(self)
        self.text13 = QLineEdit(self)
        self.text7 = QLineEdit(self)
        self.text8 = QLineEdit(self)
        self.text12 = QLineEdit(self)
        self.text9 = QLineEdit(self)
        self.text11 = QLineEdit(self)
        self.text14 = QLineEdit(self)
        self.text16 = QLineEdit(self)
        self.text17 = QLineEdit(self)
        self.text18 = QLineEdit(self)
        self.text1 = QLineEdit(self)
        self.text4 = QLineEdit(self)
        self.text6 = QLineEdit(self)
        self.text5 = QLineEdit(self)
        self.text3 = QLineEdit(self)
        self.text2 = QLineEdit(self)
        self.check2 = QCheckBox("AST", self)
        self.check4 = QCheckBox("ASV", self)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button1)
        layout.addWidget(self.button2)
        layout.addWidget(self.text15)
        layout.addWidget(self.text13)
        layout.addWidget(self.text7)
        layout.addWidget(self.text8)
        layout.addWidget(self.text12)
        layout.addWidget(self.text9)
        layout.addWidget(self.text11)
        layout.addWidget(self.text14)
        layout.addWidget(self.text16)
        layout.addWidget(self.text17)
        layout.addWidget(self.text18)
        layout.addWidget(self.text1)
        layout.addWidget(self.text4)
        layout.addWidget(self.text6)
        layout.addWidget(self.text5)
        layout.addWidget(self.text3)
        layout.addWidget(self.text2)
        layout.addWidget(self.check2)
        layout.addWidget(self.check4)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.button1.clicked.connect(self.on_start)
        self.button2.clicked.connect(self.on_stop)

    def on_start(self):
        self.label.setText("Status: Running")
        self.button1.setEnabled(False)
        self.button2.setEnabled(True)
        self.text15.setText("Initiation")

        port = 1
        self.Init_COM(port)
        self.Init_Gen()

        self.Freq = float(self.text13.text())
        self.SendCommand("APPL:SQU " + str(self.Freq))

        self.Set_Amplitude(self.Vmax)
        self.DCmode = False

        fold = self.text7.text()
        basename = self.text8.text()
        foldname = fold + basename

        self.TemRes = 100
        it = 1

        while self.Temperature[it] != 999:
            self.SetT = self.Temperature[it]
            t_name = foldname + "T" + str(int(self.Temperature[it] * self.TemRes + 1 / self.TemRes))
            self.Out_Data = t_name + ".dat"
            self.Set_Temp(self.SetT)

            if it != 1:
                self.Waiting(self.Temp_Wait)

            self.text15.setText("Waiting for Temperature")
            self.CurrentT = self.Read_Temp()

            if abs(self.SetT - self.CurrentT) > self.Accuracy and self.text12.text() != "":
                self.WaitTemp()

            iv = 1
            while self.Voltage[iv] != 99999:
                self.Set_Amplitude(self.Voltage[iv] / self.AmpGain)
                time.sleep(1)
                self.text15.setText("V circle")
                time.sleep(self.WaitV / 1000.0)
                self.SaveSpec("T" + str(self.SetT) + "V" + str(self.Voltage[iv]))

                iv += 1

            if self.WaitingVoltage != 0:
                self.Set_Amplitude(self.WaitingVoltage / self.AmpGain)

            it += 1

        if self.LastTemp != 0:
            self.Set_Temp(self.LastTemp)

        self.Close_COM()
        self.label.setText("Status: Completed")

    def on_stop(self):
        self.label.setText("Status: Stopped")
        self.button1.setEnabled(True)
        self.button2.setEnabled(False)

    def Init_COM(self, port):
        pass  # Implement the COM port initialization using pyserial or another method

    def Init_Gen(self):
        self.Gen_id = 1  # Dummy implementation

    def SendCommand(self, command):
        pass  # Implement the function to send commands to the device

    def Set_Amplitude(self, amplitude):
        pass  # Implement the function to set amplitude

    def Set_Temp(self, temp):
        pass  # Implement the function to set temperature

    def Read_Temp(self):
        return 25.0  # Dummy implementation to read temperature

    def SaveSpec(self, comment):
        pass  # Implement the function to save the spectrum

    def Waiting(self, min):
        sec = round(min * 60)
        for i in range(sec):
            time.sleep(1)
            self.text15.setText(f"Waiting for {sec - i} seconds")
            QApplication.processEvents()

    def WaitTemp(self):
        while abs(self.SetT - self.CurrentT) > self.Accuracy:
            time.sleep(1)
            self.text15.setText(f"Waiting for Accuracy: {self.CurrentT}")
            self.CurrentT = self.Read_Temp()
            QApplication.processEvents()

    def Fill_Volt(self, tlist):
        tl = tlist.strip()
        p1 = 1
        vmax = 0
        pos = 0
        i1 = 0

        while p1 > 0:
            i1 += 1
            p1 = tl.find(",")
            p2 = tl.find("/")

            if p1 > 0 or p2 > 0:
                if p1 != 0:
                    vl1 = tl[:p1]
                    tl = tl[p1 + 1:]
                else:
                    vl1 = tl

                p2 = vl1.find("/")
                if p2 != 0:
                    vol1 = int(vl1[:p2])
                    vl1 = vl1[p2 + 1:]
                    p2 = vl1.find("/")
                    vols = int(vl1[:p2])
                    vol2 = int(vl1[p2 + 1:])
                    if vol1 > vol2:
                        vols = -vols

                    for vol in range(vol1, vol2, vols):
                        self.Voltage[i1] = vol
                        i1 += 1

                    i1 -= 1
                else:
                    self.Voltage[i1] = int(vl1)
                    if self.Voltage[i1] > vmax:
                        vmax = self.Voltage[i1]
            else:
                self.Voltage[i1] = int(tl)
                if self.Voltage[i1] > vmax:
                    vmax = self.Voltage[i1]

        self.Num_Volt = i1
        self.Voltage[i1 + 1] = 99999

    def Fill_Temp(self, tlist):
        tl = tlist.strip()
        p5 = 1
        pos = 0
        i5 = 0

        while p5 > 0:
            i5 += 1
            p5 = tl.find(",")
            p6 = tl.find("/")

            if p5 > 0 or p6 > 0:
                if p5 != 0:
                    tl1 = tl[:p5]
                    tl = tl[p5 + 1:]
                else:
                    tl1 = tl

                p6 = tl1.find("/")
                if p6 != 0:
                    tem1 = int(tl1[:p6])
                    tl1 = tl1[p6 + 1:]
                    p6 = tl1.find("/")
                    tems = int(tl1[:p6])
                    tem2 = int(tl1[p6 + 1:])
                    if tem1 > tem2:
                        tems = -tems

                    for tem in range(tem1, tem2, tems):
                        self.Temperature[i5] = tem
                        i5 += 1

                    i5 -= 1
                else:
                    self.Temperature[i5] = int(tl1)
            else:
                self.Temperature[i5] = int(tl)

        self.Num_Temp = i5
        self.Temperature[i5 + 1] = 999


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
