from agent import Agent
import constants as consts
import numpy as np

class DishWasherCycle():
    ECO = {
        'name' : 'Eco',
        'power': [10, 10, 100, 1830, 90, 90, 90, 100, 1790, 1790]
    }

    VERY_DIRTY = {
        'name' : 'Very Dirty',
        'power': [1840, 1830, 1840, 1850, 1830, 1850, 1860]
    }

class DishWasher(Agent):
    def __init__(self, id, addr, port, simulation = False):
        super().__init__(id, addr, port, simulation)
        self.name               = "DishWasher"
        self.timeToEndBefore    = None
        self.timeToStartAfter   = None
        self.cycle              = DishWasherCycle.ECO

        self.startDaemonThread(simulation)

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
        if (time > consts.kTIME_SLOTS):
            return False
        self.timeToEndBefore = time

    def startAfter(self, time):
        if (time >= consts.kTIME_SLOTS):
            return False
        if (time < 0):
            return False

        self.timeToStartAfter = time

    def removeTimeToEndBefore(self):
        self.timeToEndBefore = None

    def removeTimeToStartAfter(self):
        self.timeToStartAfter = None

    def packDataForWebServer(self):
        if self.value is not None:
            start_timestep = int(self.value)
        else:
            start_timestep = 0
        cycle = self.getCycle()

        cycle_length = len(cycle)
        sending_cycle = [0] * consts.kTIME_SLOTS
        sending_cycle[start_timestep:cycle_length + start_timestep] = cycle

        data = {
            "name"  : self.name,
            "id"    : self.id,
            "start" : start_timestep,
            "end"   : start_timestep + cycle_length,
            "cycle" : list(sending_cycle),
            "ip"    : self.host
        }

        return data

    def generateConfigurationForWebServer(self):
        current_cycle_name = ""
        cycles = [name for name, value in vars(DishWasherCycle).items() if not name.startswith('_')]
        for c in cycles:
            if self.cycle['name'] == getattr(DishWasherCycle, c)['name']:
                current_cycle_name = c
                break

        possible_values = {}
        possible_values['cycle']        = { 'display_name' : 'Cycle',
                                            'values' : ['ECO', 'VERY_DIRTY'],
                                            'current' : current_cycle_name,
                                            'type' : 'select' }

        curr_timeToStartAfter = self.timeToStartAfter
        if curr_timeToStartAfter is None:
            curr_timeToStartAfter = 0

        possible_values['start_after']  = { 'display_name' : 'Starting Time',
                                            'values' : list(range(0, consts.kTIME_SLOTS+1)),
                                            'current' : curr_timeToStartAfter,
                                            'type' : 'timestep' }

        curr_timeToEndBefore = self.timeToEndBefore
        if curr_timeToEndBefore is None:
            curr_timeToEndBefore = consts.kTIME_SLOTS

        possible_values['end_before']   = { 'display_name' : 'Ending Time',
                                            'values' : list(range(0, consts.kTIME_SLOTS+1)),
                                            'current' : curr_timeToEndBefore,
                                            'type' : 'timestep' }

        self.writeOnFileConfigurationForWebServer(possible_values)

    def readAgentConfigurationFromWebServer(self):
        super().readAgentConfigurationFromWebServer()

        if self.jsonConfiguration is not None:
            if "cycle" in self.jsonConfiguration:
                self.cycle = getattr(DishWasherCycle, str(self.jsonConfiguration['cycle']) )
                self.debug("Ciclo impostato a {}".format(str(self.jsonConfiguration['cycle'])))

            if "end_before" in self.jsonConfiguration:
                self.endsBefore( int(self.jsonConfiguration["end_before"]) )
                self.debug("Ends before {}".format( self.timeToEndBefore ))

            if "start_after" in self.jsonConfiguration:
                self.startAfter( int(self.jsonConfiguration["start_after"]) )
                self.debug("Start after {}".format( self.timeToStartAfter ))