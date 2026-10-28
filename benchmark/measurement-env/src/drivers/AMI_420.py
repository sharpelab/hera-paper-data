import time
from qcodes import VisaInstrument

class AMI_420(VisaInstrument):
    _STATES = {
        1: 'RAMPING', 
        2: 'HOLDING', 
        3: 'PAUSED', 
        4: 'MANUAL UP', 
        5: 'MANUAL DOWN', 
        6: 'TO ZERO', 
        7: 'QUENCH DETECTED', 
        8: 'HEATING SWITCH', 
        9: 'AT ZERO'}

    def __init__(self, name, address, **kwargs):
        super().__init__(name, address, terminator='\n')
        
    def heater_on(self):
        self.write('PS 1')
        time.sleep(1)
        while int(self.ask('STATE?').strip()) == 8:
            time.sleep(5)
        
    def heater_off(self):
        self.write('PS 0')
        time.sleep(5)
        
    def state(self):
        state_id = int(self.ask('STATE?').strip())
        # return self._STATES.get(state_id, f'UNKNOWN({state_id})')
        return self._STATES[state_id]
    
    def set_setpoint(self, setpoint):
        self.write(f'CONF:FIELD:PROG {setpoint}')
    
    def ramp(self):
        self.write('RAMP')

    def mag(self, v, retries=3):
        while retries > 0:
            try:
                self.set_setpoint(v)
                time.sleep(0.1)
                self.ramp()
                time.sleep(0.1)
                while self.state() == 'RAMPING':
                    time.sleep(0.5)
                time.sleep(0.1)
                self.device_clear()
                time.sleep(0.1)
                break
            except Exception:
                time.sleep(0.5)
                self.device_clear()
                time.sleep(0.5)
                retries -= 1
    mag.full_name = 'mag'

    def get_setpoint(self):
        return float(self.ask('FIELD:TARG?').strip())
    
    def get_ramp_rate(self):
        return self.ask('RAMP:RATE:CURR?')
    
    def get_field(self):
        return float(self.ask('FIELD:MAG?').strip())
    
    def get_ramp_segs(self):
        return int(self.ask('RAMP:RATE:SEG?').strip())
