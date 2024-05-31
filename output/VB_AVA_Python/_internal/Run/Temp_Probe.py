import time
import serial

class Temp_Probe(): 
    def __init__(self,ui):
        self.ui = ui
        
        self.ser = serial.Serial('COM1', 9600, timeout=1) # Adjust the port and baudrate as necessary
        
    def Wait_Temp(self,SetT,Accuracy):
        
        self.Mess = "Waiting for Accuracy"
        i = 0
        self.CurrentT = self.Read_Temp()
        while abs(SetT - self.CurrentT) > Accuracy:
            time.sleep(1)
            self.ui.Status.setText(f"{self.Mess} {i} sec") # Used if you have a PyQt application running
            self.ui.Status.update()
            i += 1
            self.CurrentT = self.Read_Temp()
        time.sleep(3)
            
        
            
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

        ADDRESS = 1
        CODE = 3
        A1_H = 0
        A1_L = 1  # 1- Display; 2-SetPoint
        N_H = 0
        N_L = 1
        TemRes = 100  # Define the temperature resolution variable 
        
        self.ser.reset_input_buffer()
        time.sleep(0.1)
        
        message = chr(ADDRESS) + chr(CODE) + chr(A1_H) + chr(A1_L) + chr(N_H) + chr(N_L)
        message = self.Crc(message)
        
        self.ser.write(message.encode('latin-1'))
        time.sleep(0.1)
        mes = self.ser.read(7)  # Adjust the number of bytes to read if necessary
        if len(mes) < 7:
            raise Exception("Incomplete message received for Temperature")
        
        read_temp = (256 * (mes[3]) + (mes[4])) / TemRes
        
        
        return read_temp
         
    def Set_Temp(self,temp):

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
        
        self.ser.write(message.encode("latin-1"))
        time.sleep(0.2)
        
        return 1
       
              
class Mock_Temp_Probe():
    def __init__(self,ui): #Use ui if you have a UI interface
        self.ui = ui
    def Wait_Temp(self,SetT,Accuracy):
        self.Mess = "Waiting for Accuracy"
        i = 0
        self.CurrentT = self.Read_Temp()
        while abs(SetT - self.CurrentT) > Accuracy:
            time.sleep(1)
            self.ui.Status.setText(f"{self.Mess} {i} sec")
            self.ui.Status.update()
            self.ui.Temp_Label.setText(f"{self.CurrentT}")
            self.ui.Temp_Label.update()
            i += 1
            self.CurrentT = SetT
            
    
    def Read_Temp(self):
        return 20.0
             
    def Set_Temp(self,temp):
        return 1
