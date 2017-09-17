from agent import Agent
import constants as consts
import numpy as np

class Boiler(Agent):
    def __init__(self, id, addr, port, qty = 0, simulation = False):
        super().__init__(id, addr, port, simulation)
        self.name               = "Boiler"
        self.timeToEndBefore    = None
        self.timeToStartAfter   = None
        self.min_qty = 0
        self.max_qty = 100
        self.target_qty = 0
        self.setQty(qty)

        # Fonte dati: Edison - media consumi ciclo WaterHeater 16 Giugno
        # Consuma 1150 quando è acceso
        # Per il PoliMi consuma 194, quindi si imposta 194 W
        self.power_when_on = 194  # W

        # Genero il file JSON con tutte le possibilita' per il configuratore Web
        self.generateConfigurationForWebServer()

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

    def generateConfigurationForWebServer(self):
        possible_values = {}
        possible_values['start_after'] = {'display_name': 'Starting Time',
                                          'values'      : list(range(0, consts.kTIME_SLOTS + 1)),
                                          'current'     : self.timeToStartAfter,
                                          'type'        : 'timestep'}

        possible_values['end_before'] = {'display_name': 'Ending Time',
                                         'values'      : list(range(0, consts.kTIME_SLOTS + 1)),
                                         'current'     : self.timeToEndBefore,
                                         'type'        : 'timestep'}

        possible_values['initial_qty']  = { 'display_name': 'Initial Quantity',
                                            'values' : list(range(0, self.max_qty + 1)),
                                            'current': self.qty,
                                            'type' : 'integer'}

        possible_values['target_qty'] = {   'display_name': 'Target Quantity',
                                            'values' : list(range(0, self.max_qty + 1)),
                                            'current': self.target_qty,
                                            'type' : 'integer'}

        self.writeOnFileConfigurationForWebServer(possible_values)

    def readAgentConfigurationFromWebServer(self):
        super().readAgentConfigurationFromWebServer()

        if self.jsonConfiguration is not None:

            if "end_before" in self.jsonConfiguration:
                self.endsBefore( int(self.jsonConfiguration["end_before"]) )

            if "start_after" in self.jsonConfiguration:
                self.startAfter( int(self.jsonConfiguration["start_after"]) )

            if "initial_qty" in self.jsonConfiguration:
                self.setQty( int(self.jsonConfiguration["initial_qty"]) )

            if "max_qty" in self.jsonConfiguration:
                self.max_qty = int( self.jsonConfiguration["max_qty"] )

            if "target_qty" in self.jsonConfiguration:
                self.target_qty = int( self.jsonConfiguration["target_qty"] )

            if "power_when_on" in self.jsonConfiguration:
                self.power_when_on = int( self.jsonConfiguration["power_when_on"] )