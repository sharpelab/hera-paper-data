from qcodes import VisaInstrument

class Lakeshore_335(VisaInstrument):
    # TODO: PID.
    def __init__(self, name, address, **kwargs):
        super().__init__(name, address, terminator='\r\n', **kwargs)
        self.add_parameter('sample_temperature', get_cmd='KRDG? A', get_parser=float, unit='K')
        self.add_parameter('vaporizer_temperature', get_cmd='KRDG? B', get_parser=float, unit='K')
        self.add_parameter('sample_setpoint', get_cmd='SETP? 1', get_parser=float, set_cmd='SETP 1,{:.4f}', unit='K')
        self.add_parameter('vaporizer_setpoint', get_cmd='SETP? 2', get_parser=float, set_cmd='SETP 2,{:.4f}', unit='K')
        self.add_parameter('sample_range', get_cmd='RANGE? 1', get_parser=int, set_cmd='RANGE 1,{}')
        self.add_parameter('vaporizer_range', get_cmd='RANGE? 2', get_parser=int, set_cmd='RANGE 2,{}')
        self.add_parameter('sample_power', get_cmd = 'HTR? 1', get_parser=float, set_cmd = 'OUTMODE 1,3,0,0 \r\n MOUT 1,{:.4f}', unit='%')
        self.add_parameter('vaporizer_power', get_cmd = 'HTR? 2', get_parser=float, set_cmd = 'OUTMODE 2,3,0,0 \r\n MOUT 2,{:.4f}', unit='%')
        self.add_function('set_sample_closed_loop', call_cmd = 'OUTMODE 1,1,1,0')
        self.add_function('set_vaporizer_closed_loop', call_cmd = 'OUTMODE 2,1,2,0')
        #TODO: add ramp bool command        
        self.connect_message()
        
    def off(self, heater='both'):
        if heater=='sample':
            self.sample_range(0)
        elif heater=='vaporizer':
            self.vaporizer_range(0)
        elif heater=='both':
            self.sample_range(0)
            self.vaporizer_range(0)
        else:
            print(f'Error: Unknown heater type {heater}')
    
    def set_both(self, temperature, ratio=1):
        self.sample_setpoint(temperature)
        self.vaporizer_setpoint(temperature * ratio)
        r = 3
        if temperature < 20:
            r = 1
        elif temperature < 100:
            r = 2
        self.sample_range(r)
        self.vaporizer_range(r)

    def warmup(self):
        self.sample_setpoint(300)
        self.vaporizer_setpoint(100)
        self.sample_range(3)
        self.vaporizer_range(3)
