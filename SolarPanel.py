from agent import Agent
import constants as consts
import numpy as np

"""
@TODO Dati radiazione
"""

class SolarPanel(Agent):
    def __init__(self, id, addr, port):
        super().__init__(id, addr, port)
        self.name = "SolarPanel"

        self.cycle = np.array( [-7, -2, -6, -8, -8, -8, -1, -8, -7, -1, -2, -1, -7, -4, -7, -1, -30, -3, -8, -1, -6, -4, -4, -6, -4, -2, 0, -6, -6, -4, -6, 0, -5, 0, -5, 0, 0, -5, -3, -3, -7, -3, -3, -5, -3, -2, -1, -6, -7, -2, -6, -2, -6, -6, -3, -5, -8, -5, -1, -2, -3, -7, -5, -3, -3, -4, -7, -5, -7, -5, 0, -7, -7, -3, -8, -7, -2, -8, -6, -1, 0, -2, -4, -4, -7, 0, -3, -2, -8, -7, -5, -2, -5, -2, -8, -1])
        self.isProducingPower       = True
        self.otherAgentsInfluence   = {}

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