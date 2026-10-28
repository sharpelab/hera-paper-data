from qcodes import VisaInstrument

class Terranova_906A(VisaInstrument):

    def __init__(self, name, address, **kwargs):
        super().__init__(name, address, terminator='\r\n', **kwargs)
        
        self.visa_handle.baud_rate = 9600  # Example baud rate
        self.visa_handle.parity = self.visa_handle.parity.none
        self.visa_handle.data_bits = 8
        self.visa_handle.stop_bits = self.visa_handle.stop_bits.one
        self.visa_handle.flow_control = self.visa_handle.flow_control.none

        self.add_parameter(
            "version",
            get_cmd='v',
            get_parser=str,
        )

        self.add_parameter(
            "pressure",
            get_cmd='p',
            get_parser=float,
        )

        self.add_parameter(
            "units",
            get_cmd='u',
            get_parser=str,
        )