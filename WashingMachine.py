from agent import Agent
import constants as consts
import numpy as np

class WashingMachineCycle():
    COTTON_60 = {
        'name' : 'Cotton 60',
        'power': [100, 1540, 1550, 1550, 1530, 230, 190, 280, 500, 490]
    }

    COTTON_30 = {
        'name' : 'Cotton 30',
        'power': [1550, 100, 80, 60, 60, 60, 100, 60, 280, 320, 430, 500]
    }

class WashingMachine(Agent):
    def __init__(self, id, addr, port, simulation = False):
        super().__init__(id, addr, port, simulation)
        self.name               = "WashingMachine"
        self.timeToEndBefore    = None
        self.timeToStartAfter   = None
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

        # Constraint sul iniziare dopo un certo timestep
        if self.timeToStartAfter:
            if ( x < self.timeToStartAfter ):
                return {'status': False,
                        'vars'  : np.array(vars)}

        vars[x:cycle_length+x] = cycle

        return {    'status'    : True,
                    'vars'      : np.array(vars) }

    def endsBefore(self, time):
        if (time >= consts.kTIME_SLOTS):
            return False
        self.timeToEndBefore = time

    def startAfter(self, time):
        if (time >= consts.kTIME_SLOTS):
            return False
        if (time <= 0):
            return False

        self.timeToStartAfter = time

    def removeTimeToEndBefore(self):
        self.timeToEndBefore = None

    def removeTimeToStartAfter(self):
        self.timeToStartAfter = None

    def generateConfigurationForWebServer(self):
        possible_values = {}
        possible_values['cycle']        = { 'display_name' : 'Cycle', 'values' : ['COTTON_30', 'COTTON_60'] }
        possible_values['start_after']  = { 'display_name' : 'Starting Time', 'values' : list(range(0, 25)) }
        possible_values['end_before']   = { 'display_name' : 'Ending Time', 'values' : list(range(0, 25)) }

        self.writeOnFileConfigurationForWebServer(possible_values)

    def readAgentConfigurationFromWebServer(self):
        return
        super().readAgentConfigurationFromWebServer()

        if self.jsonConfiguration is not None:
            if "cycle" in self.jsonConfiguration:
                self.cycle = getattr(WashingMachineCycle, str(self.jsonConfiguration['cycle']) )

            if "end_before" in self.jsonConfiguration:
                self.endsBefore( int(self.jsonConfiguration["end_before"]) )

            if "start_after" in self.jsonConfiguration:
                self.startAfter( int(self.jsonConfiguration["start_after"]) )