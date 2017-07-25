import pandas as pd
import numpy as np
import os
import constants as const

elettrodomestici = ['Washing Machine', 'Dish Washer', 'Water Heater', 'Fridge']
date = ['12', '13', '16', '17', '18', '24']

for data in date:
    dir         = os.path.dirname(__file__)
    data_folder = os.path.join(dir, "dati perini")
    filename    = os.path.join(data_folder, "domus power {} giugno.txt".format(data))

    df = pd.read_csv(filename, delimiter="\t")

    output_dir = os.path.join(dir, "{}_giugno".format(data))
    try:
        os.mkdir(output_dir)
    except FileExistsError:
        pass

    for elettrodomestico in elettrodomestici:

        output_filename = os.path.join(output_dir, "{}Cycle.csv".format(elettrodomestico.replace(" ", "")))

        wm = df[elettrodomestico]

        wm_cycle = []
        for t in range(1, const.kTIME_SLOTS + 1):
            start   = (t - 1) * 900
            end     = t * 900
            wm_cycle.append( max(wm[start:end]) )

        np.savetxt(output_filename, np.array( wm_cycle ), fmt='%i', delimiter=',')
