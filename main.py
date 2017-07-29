import os
import socket
import random
import time

"""
WASHING MACHINE
"""
from WashingMachine import WashingMachine
from WashingMachine import WashingMachineCycle

"""
BOILER
"""
from Boiler import Boiler

"""
SOLAR PANEL
"""
from SolarPanel import SolarPanel

"""
BATTERY
"""
from Battery import Battery

"""
Nomi Raspberry PI
"""
kRaspberryPI_1 = 'raspberrypi1'
kRaspberryPI_2 = 'raspberrypi2'

hostname = socket.gethostname()

# In base ai vari nomi dei RaspberryPi avvio diversi elettrodomestici

# Genero un ID random per l'agente OPPURE ne uso uno predefinito per ogni RaspberryPI
# random.seed( int(time.time()) )
# agent_id = int( (random.random() * random.random()) * int(time.time()))

agent = None

if hostname == kRaspberryPI_1:
    agent_id    = 1
    agent       = WashingMachine(agent_id, range(0, 96), 12345)

elif hostname == kRaspberryPI_2:
    agent_id    = 2
    agent       = Boiler(agent_id, range(0, 96), 12345)

    # Parametri del boiler
    agent.max_qty    = 100
    agent.target_qty = 90
    agent.setQty(50)

# Se ho un agente impostato, ogni 5 secondi avvio una ottimizzazione
if agent:
    while (True):
        agent.start()
        time.sleep(5.0)
else:
    print("Nessun agente impostato. Esco.")