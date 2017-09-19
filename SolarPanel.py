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
        self.cycle = np.zeros(consts.kTIME_SLOTS)

        self.radiation_type = SolarPanelRadiation.MEDIUM

        self.readRadiation()

        self.isProducingPower       = True
        self.otherAgentsInfluence   = {}

        self.startDaemonThread(simulation)

    def setRadiation(self, rad_type):
        self.radiation_type = rad_type
        self.readRadiation()

    def readRadiation(self):
        dir                             = os.path.dirname(__file__)
        solar_panel_radiation_folder    = os.path.join(dir, "solar_panel_radiation")
        file_path                       = os.path.join(solar_panel_radiation_folder, self.radiation_type)

        cycle = np.genfromtxt(file_path)
        cycle = cycle * 1.98 # Radiazione * costante

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

    def packDataForWebServer(self):
        start_timestep = 0
        end_timestep = consts.kTIME_SLOTS

        # I segni sono strani perché il ciclo ha i numeri negativi
        cycle = self.getCycle()
        for index in range(0, len(cycle)):
            if cycle[index] < 0:
                start_timestep = index
                break

        for index in range(start_timestep, len(cycle)):
            if cycle[index] >= 0:
                end_timestep = index
                break

        sending_cycle = np.absolute(cycle)

        data = {
            "name"  : self.name,
            "id"    : self.id,
            "start" : start_timestep,
            "end"   : end_timestep,
            "cycle" : list(sending_cycle),
            "ip"    : self.host
        }


        return data

    def generateConfigurationForWebServer(self):
        possible_values = {}
        self.writeOnFileConfigurationForWebServer(possible_values)

    def readAgentConfigurationFromWebServer(self):
        super().readAgentConfigurationFromWebServer()