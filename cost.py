import numpy as np
import constants as consts

def getCostsArray():
    cost = [1] * consts.kTIME_SLOTS
    return np.array( cost )