import time
import serial
class Temp_Probe(): 
    def __init__(self,mp):
        self.mp = mp
    def Wait_Temp(self):
        self.Mess = "Waiting for Accuracy"
        i = 0
        self.CurrentT = self.Read_Temp()
        while abs(self.mp.SetT - self.CurrentT) > self.Accuracy:
            time.sleep(1)
            self.mp.Status.setText(f"{self.Mess} {i} sec") # Used if you have a PyQt application running
            self.mp.Status.update()
            i += 1
            self.CurrentT = self.Read_Temp()
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
        
        
class Mock_Temp_Probe():
    def __init__(self,mp):
         self.mp = mp
    def Wait_Temp(self):
        global Accuracy
        self.Mess = "Waiting for Accuracy"
        i = 0
        self.CurrentT = self.Read_Temp()
        while abs(self.mp.SetT - self.CurrentT) > self.mp.Accuracy:
            time.sleep(1)
            self.ui.Status.setText(f"{self.Mess} {i} sec")
            self.ui.Status.update()
            i += 1
            self.CurrentT = self.mp.SetT
    
    def Read_Temp(self):
        return 20.0
             
    def Set_Temp(self,temp):
        return 1
