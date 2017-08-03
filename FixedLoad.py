import numpy as np
import os
import constants as const

global cycle
cycle = np.zeros( const.kTIME_SLOTS )

def readFixedLoad(fixed_load_file):
    global cycle

    if len(fixed_load_file) < 1:
        return False

    dir = os.path.dirname(__file__)
    solar_panel_radiation_folder = os.path.join(dir, "fixed_load")
    file_path = os.path.join(solar_panel_radiation_folder, fixed_load_file)

    cycle_raw = np.genfromtxt(file_path)
    cycle = np.array(cycle_raw)

def getCycle():
    global cycle
    return np.array( cycle )