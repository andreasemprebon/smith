import os

"""
WASHING MACHINE
"""
from WashingMachine import WashingMachine
from WashingMachine import WashingMachineCycle

"""
BOILER
"""
from Boiler import Boiler

a1 = WashingMachine(1, range(0, 96), 12346)
a2 = WashingMachine(2, range(0, 96), 12347)
a3 = Boiler(3, range(0, 96), 12348, 70)
a4 = Boiler(4, range(0, 96), 12349, 50)

a2.cycle = WashingMachineCycle.COTTON_30

a2.isRoot = False
a3.isRoot = False
a4.isRoot = False

a1.addNewDiscoveredAgent(a2.id, "127.0.0.1", a2.port)
a1.addNewDiscoveredAgent(a3.id, "127.0.0.1", a3.port)
a1.addNewDiscoveredAgent(a4.id, "127.0.0.1", a4.port)

a2.addNewDiscoveredAgent(a1.id, "127.0.0.1", a1.port)
a2.addNewDiscoveredAgent(a3.id, "127.0.0.1", a3.port)
a2.addNewDiscoveredAgent(a4.id, "127.0.0.1", a4.port)

a3.addNewDiscoveredAgent(a1.id, "127.0.0.1", a1.port)
a3.addNewDiscoveredAgent(a2.id, "127.0.0.1", a2.port)
a3.addNewDiscoveredAgent(a4.id, "127.0.0.1", a4.port)

a4.addNewDiscoveredAgent(a1.id, "127.0.0.1", a1.port)
a4.addNewDiscoveredAgent(a2.id, "127.0.0.1", a2.port)
a4.addNewDiscoveredAgent(a3.id, "127.0.0.1", a3.port)

"""
Avvio i vari agenti sulla stessa macchina
E' solamente il genitore che lancia, quindi mi salvo
in parent_pid il valore del PID del processo attuale in modo
che sia solo lui a fare la fork
"""
parent_pid = os.getpid()

children = []

#Avvio il primo processo figlio
if parent_pid == os.getpid():
    childid = os.fork()
    children.append(childid)
    if childid == 0:
        a2.start()

#Avvio il secondo processo figlio
if parent_pid == os.getpid():
    childid = os.fork()
    children.append(childid)
    if childid == 0:
        a3.start()

# Avvio il secondo processo figlio
if parent_pid == os.getpid():
    childid = os.fork()
    children.append(childid)
    if childid == 0:
        a4.start()

#Avvio il padre ed attendo che tutti i figli terminino
if parent_pid == os.getpid():
    a1.start()
    for i in children:
        os.wait()