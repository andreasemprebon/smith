from agent import Agent
import constants as consts
import numpy as np

class WashingMachineCycle():
    IDLE      = {
                    'name'  : 'idle',
                    'power' : [0]
                }
    COTTON_60 = {
                    'name'  : 'Cotton 60',
                    'power' : [10, 15, 20, 8, 5]
                }

    COTTON_30 = {
                    'name' : 'Cotton 30',
                    'power': [30, 30, 30, 8, 10, 3, 2]
                }

class WashingMachine(Agent):
    def __init__(self, id, addr, port):
        super().__init__(id, addr, port)
        self.name               = "WashingMachine"
        self.timeToEndBefore    = None
        self.cycle              = WashingMachineCycle.COTTON_60

    def getCycle(self):
        return self.cycle['power']

    def getVarsFromStartingPoint(self, x):
        vars    = [0] * consts.kTIME_SLOTS
        cycle   = self.getCycle()

        cycle_length = len(cycle)

        if ( cycle_length + x > consts.kTIME_SLOTS ):
            return {    'status'    : False,
                        'vars'      : np.array(vars) }

        # Constraint sul finire entro un certo tempo
        if self.timeToEndBefore:
            if ( cycle_length + x > self.timeToEndBefore ):
                return {'status': False,
                        'vars'  : np.array(vars)}

        vars[x:cycle_length+x] = cycle

        return {    'status'    : True,
                    'vars'      : np.array(vars) }

    def endsBefore(self, time):
        if (time >= consts.kTIME_SLOTS):
            return False
        self.timeToEndBefore = time

    def removeTimeToEndBefore(self):
        self.timeToEndBefore = None