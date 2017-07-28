from agent import Agent
import constants as consts
import numpy as np

class DishWasherCycle():
    ECO = {
            'name'  : 'Eco',
            'power' : [10, 15, 20, 8, 5]
            }

    VERY_DIRTY = {
                    'name' : 'Very Dirty',
                    'power': [30, 30, 30, 8, 10, 3, 2]
                }

class DishWasher(Agent):
    def __init__(self, id, addr, port):
        super().__init__(id, addr, port)
        self.name               = "DishWasher"
        self.timeToEndBefore    = None
        self.timeToStartAfter   = None
        self.cycle              = DishWasherCycle.ECO

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