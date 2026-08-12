""" from Visual_Basic_Python import MainProgram """

class Generator():
    """Main Generator class"""
    def __init__(self, rm):
        B_G = 0
        P_G = 10
        N_G = 0
        T_G = 0
        E1_G = 1
        E2_G = 0
        self.rm = rm
        # gpib_address = f"FPIB{B_G}::{P_G}::{N_G}::INSTR"
        gpib_address = "GPIB0::10::INSTR"
        print("Connected to generator")
        self.gen = self.rm.open_resource(gpib_address)

        # ser = serial.Serial("COM1",9600,timeout = 3)
        self.Set_Offset("0")
    def Set_Offset(self,offset):
        command = f"VOLT:OFFS {offset}\n"
        self.send_command(command)

    def send_command(self,command):
        if self.gen is not None:
            self.gen.write(command)
        else:
            raise Exception("No connection on GPIB")

    def Set_Waveform(self,form):
        command = f"FUNC:SHAP {form}\n"
        self.send_command(command)
    def Set_Freq(self,freq):
        command = f"FREQ {freq}"
        self.send_command(command)
    def Set_Amplitude(self,amplitude, freq, DCmode):
        
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

class Mock_Generator():
    def __init__(self):
        # ser = serial.Serial("COM1",9600,timeout = 3)
        self.Set_Offset("0")
        return
    def Set_Offset(self,offset):
        return

    def send_command(self,command):
        return

    def Set_Waveform(self,form):
        return
    def Set_Freq(self,freq):
        return
    def Set_Amplitude(self,amplitude, freq,Dcmode):
        return
