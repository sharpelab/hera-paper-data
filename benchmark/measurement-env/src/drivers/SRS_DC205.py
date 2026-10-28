import numpy as np
from qcodes import VisaInstrument
from time import sleep

class SRS_DC205(VisaInstrument):
    # driver for SRS DC source
    def __init__(self, name, address, **kwargs):
        super().__init__(name, address, terminator='\r\n', **kwargs)
        self.add_parameter('output', get_cmd='SOUT?', get_parser=int, set_cmd='SOUT {}')
        self.add_parameter('voltage', label="Voltage", unit = "V", get_cmd='VOLT?', get_parser=float, set_cmd='VOLT {}')
        self.add_parameter('voltage_range', label="Voltage Range", unit = "V", get_cmd='RNGE?', get_parser=int, set_cmd='RNGE {}')
        # note that for voltage range 0 : +- 1V, 1 : +- 10V, 2 : +- 100V
        
        self.add_parameter("smart_voltage",label="smart voltage", unit="V", get_cmd="VOLT?", get_parser=float, set_cmd=self.ramp_voltage)
        self.visa_handle.baud_rate = 115200
        self.ramp_num_points = 50
        self.ramp_wait_time = 0.01
        self.ramp_rate = 5
        self.connect_message()
    
    def ramp_voltage(self, final_volt):
        """
        Ramp to a specified voltage from the current voltage
        """
        starting_volt = self.voltage()
        ramp_time = np.abs(starting_volt-final_volt)/self.ramp_rate
        self.ramp_wait_time = ramp_time/self.ramp_num_points
        voltage_vec = np.linspace(starting_volt, final_volt, self.ramp_num_points)
        for v in voltage_vec:
            self.voltage(np.round(v,9))
            # rounding is because the instrument does not like numbers with too many decimals
            sleep(self.ramp_wait_time)
        
        # mandatory sleep for large ramps in voltage
        # if abs(final_volt - starting_volt) > 0.1:
        #     sleep(10)