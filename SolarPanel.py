from agent import Agent
import constants as consts
import numpy as np
import os

class SolarPanelRadiation():
    LOW     = "low.csv"
    MEDIUM  = "medium.csv"
    HIGH    = "high.csv"

class SolarPanel(Agent):
    def __init__(self, id, addr, port, simulation = False):
        super().__init__(id, addr, port, simulation)
        self.name = "SolarPanel"

        self.radiation_type = SolarPanelRadiation.MEDIUM

        self.readRadiation()

        self.isProducingPower       = True
        self.otherAgentsInfluence   = {}

    def setRadiation(self, rad_type):
        self.radiation_type = rad_type
        self.readRadiation()

    def readRadiation(self):
        dir                             = os.path.dirname(__file__)
        solar_panel_radiation_folder    = os.path.join(dir, "solar_panel_radiation")
        file_path                       = os.path.join(solar_panel_radiation_folder, self.radiation_type)

        cycle = np.genfromtxt(file_path)
        cycle = cycle * 1.98 * 0.866 # Radiazione * costante * cos(30)

        self.cycle  = np.array(cycle)

        if (len(self.cycle) != consts.kTIME_SLOTS):
            raise ValueError("Il vettore con la produzione del pannello solare non è della lunghezza corretta.")

    def getCycle(self):
        return self.cycle

    def getVarsFromStartingPoint(self, x):
        return {    'status'    : True,
                    'vars'      : np.array(self.cycle) }

    def getAvailPowerFromStartingPoint(self, x, other_agent):
        vars = np.array( self.cycle )

        # Le mie variabili sono negative, in quanto immetto potenza nel sistema,
        # sommo quindi le potenze degli altri agenti che ho già considerato.
        # Se la somma è positiva, allora la metto a 0, altrimenti lascio il valore.
        # In relations poi verrà aggiunto anche il contributo dell'agente considerato
        for id in self.otherAgentsInfluence:
            if id != other_agent:
                a = self.otherAgentsInfluence[id]
                vars = np.array(vars) + a.getVarsFromStartingPoint(x)['vars']

        vars[np.where(vars > 0)] = 0

        return {'status': True,
                'vars'  : np.array(vars)}