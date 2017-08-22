from agent import Agent
import constants as consts
import numpy as np
import os

class FixedLoad(Agent):
    def __init__(self, id, addr, port, simulation = False):
        super().__init__(id, addr, port, simulation)
        self.name = "FixedLoad"
        self.cycle = np.zeros( consts.kTIME_SLOTS )

    def readFixedLoad(self, fixed_load_file):
        if len(fixed_load_file) < 1:
            return False

        dir = os.path.dirname(__file__)
        fixed_load_file_folder = os.path.join(dir, "fixed_load")
        file_path = os.path.join(fixed_load_file_folder, fixed_load_file)

        cycle_raw = np.genfromtxt(file_path)
        self.cycle = np.array(cycle_raw)

        if (len(self.cycle) != consts.kTIME_SLOTS):
            raise ValueError("Il vettore con il carico fisso non è della lunghezza corretta.")

    def getCycle(self):
        return self.cycle

    def getVarsFromStartingPoint(self, x):
        return {    'status'    : True,
                    'vars'      : np.array(self.cycle) }