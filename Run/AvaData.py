import time
import psutil
import subprocess
import pyautogui
import pygetwindow as gw
import matplotlib.pyplot as plt

class AppControl():
    ### Window Control ### 
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
    
# class DirectControl:
#     def __init__(self):
#         AVS_Init(0)
#         USBDevices = AVS_UpdateUSBDevices()
#         print("Number of Devices connected", USBDevices)
#         device_list = AVS_GetList()
#         if device_list:
#             self.deviceId = device_list[0]
#             print(self.deviceId)
#             self.AVS_Handle = AVS_Activate(self.deviceId)
#             print("Handle:",self.AVS_Handle)
#         else:
#             raise Exception("No devices found")
#     def Configuration(self):
#         measconfig = MeasConfigType()
#         measconfig.m_StartPixel = 0
#         measconfig.m_StopPixel = 2046
#         measconfig.m_IntegrationTime = float(0.1)
#         measconfig.m_IntegrationDelay = 0
#         measconfig.m_NrAverages = int(12)
#         measconfig.m_CorDynDark_m_Enable = 0  # nesting of types does NOT work!!
#         measconfig.m_CorDynDark_m_ForgetPercentage = 0
#         measconfig.m_Smoothing_m_SmoothPix = 0
#         measconfig.m_Smoothing_m_SmoothModel = 0
#         measconfig.m_SaturationDetection = 0
#         measconfig.m_Trigger_m_Mode = 0
#         measconfig.m_Trigger_m_Source = 0
#         measconfig.m_Trigger_m_SourceType = 0
#         measconfig.m_Control_m_StrobeControl = 0
#         measconfig.m_Control_m_LaserDelay = 0
#         measconfig.m_Control_m_LaserWidth = 0
#         measconfig.m_Control_m_LaserWaveLength = 0.0
#         measconfig.m_Control_m_StoreToRam = 0
#         return measconfig

#     def measure_cb(self, pparam1, pparam2):
#             param1 = pparam1[0] # dereference the pointers
#             param2 = pparam2[0]
#             self.newdata.emit(param1, param2) 
            
            
#     def GetData(self):
#         test1 = AVS_PrepareMeasure(self.AVS_Handle,self.Configuration())
#         print("Prepare:",test1)
#         avs = AVS_Measure(self.AVS_Handle, 0, -1)
#         time.sleep(3)
#         if avs != 0:
#             print(avs)
#             raise Exception("No measurement found")
#         # avs_cb = AVS_MeasureCallbackFunc(self.measure_cb)
#         # l_Res = AVS_MeasureCallback(self.AVS_Handle, avs_cb, 1)
#         # if (0 != l_Res):
#         #     print("AVS_MeasureCallback failed, error: {0:d}".format(l_Res)) 
#         # time.sleep(2)
#         if AVS_PollScan(self.AVS_Handle) == 1:
#             timestamp, spectraldata = AVS_GetScopeData(self.AVS_Handle)
#             wavelength = AVS_GetLambda(self.AVS_Handle)
#             print("Data", spectraldata)
#             return wavelength , spectraldata
#         else:
#             print("no data found")
            
        

#     def Print(self, wavelength,spectraldata):
#         pixels = len(spectraldata)
#         x = wavelength
#         # y = [67000.0 - spectraldata[i] for i in range(pixels)]
#         y = spectraldata
#         plt.plot(x, y, ".")
#         plt.xlabel('Wavelenggth')
#         plt.ylabel('Intensity')
#         plt.title('Spectral Data')
#         plt.show()
        
#         AVS_StopMeasure(self.AVS_Handle)
#         AVS_Done()

