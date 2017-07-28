import numpy as np
import constants as consts
import requests
import os
from lxml import etree

### SCARICO IL FILE

# url = "http://www.mercatoelettrico.org/It/WebServerDataStore/MGP_Prezzi/20170726MGPPrezzi.xml"
#
# req_prezzo_xml = requests.get(url)
# prezzo_xml = req_prezzo_xml.text
# req_prezzo_xml.close()
# tree = etree.parse(prezzo_xml)

global cost
cost = []

def readCostFromFile( cost_file ):
    global cost
    dir             = os.path.dirname(__file__)

    output_folder   = os.path.join(dir, "output")
    cost_output     = os.path.join(output_folder, "cost.csv")

    ### LEGGO IL FILE

    input_folder    = os.path.join(dir, "gme")
    filename        = os.path.join(input_folder, cost_file)

    # Leggo il file XML
    tree = etree.parse(filename)

    # Ottengo la root
    prezzi_root = tree.getroot()

    prezzi = prezzi_root.findall("./Prezzi")

    tmp_cost = {}
    for prezzo in prezzi:
        ora = int( prezzo.find("Ora").text )
        pun = prezzo.find("PUN").text
        pun = pun.replace(",", ".")
        costo = float( pun )
        tmp_cost[ora - 1] = costo


    ord_cost = []
    for ora in sorted(tmp_cost):
        ord_cost.append( tmp_cost[ora] )

    ord_cost = np.array( ord_cost )

    cost = []
    for t in range(0, consts.kTIME_SLOTS):
        index = int( np.floor( t / 4 ) )
        cost.append( ord_cost[index] )

    cost = np.array( cost )

    if len(cost) != consts.kTIME_SLOTS:
        raise ValueError("Il vettore di costo ha una dimensione errata")

    np.savetxt(cost_output, cost, fmt='%.2f', delimiter=',')

#readCostFromFile("20170725MGPPrezzi.xml")

def getCostsArray():
    global cost
    return np.array( cost )