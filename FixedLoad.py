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

    output_folder       = os.path.join(dir, "output")
    fixed_load_output   = os.path.join(output_folder, "fixed_load_cycle.csv")

    cycle_raw = np.genfromtxt(file_path)
    cycle = np.array(cycle_raw)

    np.savetxt(fixed_load_output, cycle, fmt='%.2f', delimiter=',')

def getCycle():
    global cycle
    return np.array( cycle )