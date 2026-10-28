from qcodes import VisaInstrument

class AMI_1700(VisaInstrument):
    def __init__(self, name, address, **kwargs):
        super().__init__(name, address, terminator='\r\n', **kwargs)
        self.add_parameter('He_level', get_cmd='MEAS:HE:LEV?', get_parser=float, unit='in')