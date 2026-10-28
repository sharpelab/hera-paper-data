from qcodes import VisaInstrument

class Lakeshore_218(VisaInstrument):
    # TODO: PID.
    def __init__(self, name, address, **kwargs):
        super().__init__(name, address, terminator='\r\n', **kwargs)
        self.add_parameter('magnet_temperature', get_cmd='KRDG? 1', get_parser=float, unit='K')
        self.add_parameter('gm_temperature', get_cmd='KRDG? 5', get_parser=float, unit='K')
        self.connect_message()