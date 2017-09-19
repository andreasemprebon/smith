import os
import socket
import time
import cost
import threading

"""
WASHING MACHINE
"""
from WashingMachine import WashingMachine
from WashingMachine import WashingMachineCycle

"""
DISH WASHER
"""
from DishWasher import DishWasher
from DishWasher import DishWasherCycle

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
COST
"""
cost_filename = "20170725MGPPrezzi.xml"
cost.readCostFromFile( cost_filename )

"""
Nomi Raspberry PI
"""
kRaspberryPI_1 = 'raspberrypi1'
kRaspberryPI_2 = 'raspberrypi2'
kRaspberryPI_3 = 'raspberrypi3'
kRaspberryPI_4 = 'raspberrypi4'
kRaspberryPI_5 = 'raspberrypi5'

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

elif hostname == kRaspberryPI_3:
    agent_id    = 3
    agent       = DishWasher(agent_id, range(0, 96), 12345)

    # La lavastoviglie inizia dopo il time step 30
    agent.startAfter( 30 )

elif hostname == kRaspberryPI_4:
    agent_id    = 4
    agent       = SolarPanel(agent_id, range(0, 96), 12345)

elif hostname == kRaspberryPI_5:
    agent_id    = 5
    agent       = Battery(agent_id, range(0, 96), 12345)
else:
    agent_id = 99
    agent =  WashingMachine(agent_id, range(0, 96), 12345)

# Elimina il file di configurazione WEB
try:
    content_folder = os.path.join("/", "var", "www", "html", "api")
    conf_file = os.path.join(content_folder, "conf.json")
    os.unlink(conf_file)
except:
    pass

# Se ho un agente impostato, ogni 5 secondi avvio una ottimizzazione
if agent:
    while (True):
        agent.generateConfigurationForWebServer()
        agent.readAgentConfigurationFromWebServer()

        t = threading.Thread( target=agent.start )
        t.setDaemon(True)
        t.start()

        start_time = time.time()

        while (True):
            t.join(timeout = 5)
            elapsed_time = time.time() - start_time
            if elapsed_time > 60: #Dopo un minuto di ottimizzazione chiudo il thread e lo riapro
                agent.killStartThread = True


            if t.is_alive():
                if agent.removeOldDiscoveredAgent():
                    agent.killStartThread = True
                    agent.debug("Stop del thread start")
            else:
                break

        #agent.start()
        time.sleep(5.0)
else:
    print("Nessun agente impostato. Esco.")