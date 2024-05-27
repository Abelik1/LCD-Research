import unittest
from unittest.mock import MagicMock, patch

# Assume MainProgram contains the Generator class

from generator import Generator
DCmode = False
class TestGenerator(unittest.TestCase):
    def setUp(self):
        # Mock the Resource Manager
        self.mock_rm = MagicMock()
        self.mock_gen = MagicMock()
        self.mock_rm.open_resource.return_value = self.mock_gen

        self.generator = Generator(self.mock_rm)

    def test_connection(self):
        # Ensure the resource manager's open_resource was called correctly
        self.mock_rm.open_resource.assert_called_with("GPIB0::10::INSTR")
        print("test_connection passed")

    def test_set_offset(self):
        self.generator.Set_Offset("5")
        self.mock_gen.write.assert_called_with("VOLT:OFFS 5\n")
        print("test_set_offset passed")

    def test_send_command(self):
        self.generator.send_command("TEST COMMAND")
        self.mock_gen.write.assert_called_with("TEST COMMAND")
        print("test_send_command passed")

    def test_set_waveform(self):
        self.generator.Set_Waveform("SIN")
        self.mock_gen.write.assert_called_with("FUNC:SHAP SIN\n")
        print("test_set_waveform passed")

    def test_set_freq(self):
        self.generator.Set_Freq("1000")
        self.mock_gen.write.assert_called_with("FREQ 1000")
        print("test_set_freq passed")

    def test_set_amplitude(self):

        self.generator.Set_Amplitude("5", "1000", False)
        self.mock_gen.write.assert_any_call("VOLT 5\n")
        print("test_set_amplitude (non-zero) passed")

        DCmode = False
        self.generator.Set_Amplitude(0, "1000", DCmode)
        self.mock_gen.write.assert_called_with("APPLy:DC DEF, DEF, O\n")
        print("test_set_amplitude (zero) passed")

if __name__ == '__main__':
    unittest.main()
