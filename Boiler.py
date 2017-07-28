from agent import Agent
import constants as consts
import numpy as np

class Boiler(Agent):
    def __init__(self, id, addr, port, qty = 0):
        super().__init__(id, addr, port)
        self.name               = "Boiler"
        self.timeToEndBefore    = None
        self.timeToStartAfter   = None
        self.min_qty = 0
        self.max_qty = 100
        self.target_qty = 0
        self.setQty(qty)

        # Consuma 10 quando è acceso
        self.power_when_on = 10

    # Imposta la quantità di acqua calda presente nel boiler
    def setQty(self, val):
        qty = max(val, self.min_qty)
        qty = min(qty, self.max_qty)
        self.qty = qty

    # A partire da una certa quantità di acqua resituisce il tempo (misurato in numero di time step)
    # necessario per raggiungere una quantità target
    def getTimeToReachQty(self, target_qty):
        if target_qty <= self.qty:
            return 0
        else:
            return np.floor((target_qty - self.qty) / 5).astype(int)

    def getCycle(self):
        duration = self.getTimeToReachQty( min(self.target_qty, self.max_qty) )
        return [self.power_when_on] * duration

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
            if (x < self.timeToStartAfter):
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
