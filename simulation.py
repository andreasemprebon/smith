import os
import sys
import json
from shutil import move, rmtree
import numpy as np
import constants as const
from collections import OrderedDict
import timeit

"""
FIXED LOAD
"""
import FixedLoad

"""
COSTO
"""
import cost

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
from SolarPanel import SolarPanelRadiation

"""
BATTERY
"""
from Battery import Battery

def printTitle( string ):
    print( "#" * (len(string) + 8) )
    print( "### {} ###".format(string))
    print( "#" * (len(string) + 8) )

dir                         = os.path.dirname(__file__)
simulation_scenario_folder  = os.path.join(dir, "simulation_scenario")

# Controllo che lo scenario esista e sia lanciabile

if len(sys.argv) <= 1:
    raise AttributeError("Utilizzo: python simulation.py file_scenario.json")

scenario = sys.argv[1]
nome_scenario = os.path.splitext(scenario)[0]

scenario_file = os.path.join(simulation_scenario_folder, scenario)

if not os.path.isfile( scenario_file ):
    raise FileNotFoundError("Il file scenario passato non esiste nella cartella simulation_scenario")

# Leggo file simulazione

with open(scenario_file) as data_file:
    data = json.load(data_file)

printTitle( "Avvio simulazione {}".format(nome_scenario) )

# Elimino i vecchi file di output

output_folder           = os.path.join(dir, "output")

try:
    os.mkdir(output_folder)
except FileExistsError:
    pass

scenario_output_folder  = os.path.join(output_folder, nome_scenario)

try:
    os.mkdir(scenario_output_folder)
except FileExistsError:
    rmtree(scenario_output_folder, ignore_errors = True)
    os.mkdir(scenario_output_folder)
    pass

for the_file in os.listdir(output_folder):
    file_path = os.path.join(output_folder, the_file)
    try:
        if os.path.isfile(file_path):
            os.unlink(file_path)
    except Exception as e:
        print(e)

# Creo una simulazione per ciascun giorno e la lancio:

for day, desc in enumerate( data['days'] ):
    # Dati per la comunicazione
    agents      = []
    port_number = 12300
    id_number   = 1

    printTitle( "Giorno {}".format(day) )

    # Imposto il file di costo corretto
    cost.readCostFromFile( desc['cost_file'] )

    print("\tFile costo associato: {}".format(desc['cost_file']) )

    # Imposto gli agenti
    for agent in desc['agents']:

        agent_type = str(agent["type"]).lower()
        ag = None

        print("\tCreo agente {} con id {}".format(str(agent["type"]), id_number))

        if agent_type == "washingmachine":
            ag =  WashingMachine(id_number, range(0, 96), port_number, simulation=True)

            if "cycle" in agent:
                ag.cycle = getattr(WashingMachineCycle, str(agent['cycle']) )

            if "end_before" in agent:
                ag.endsBefore( int(agent["end_before"]) )

            if "start_after" in agent:
                ag.startAfter( int(agent["start_after"]) )

        elif agent_type == "dishwasher":
            ag =  DishWasher(id_number, range(0, 96), port_number, simulation=True)

            if "cycle" in agent:
                ag.cycle = getattr(DishWasherCycle, str(agent['cycle']) )

            if "end_before" in agent:
                ag.endsBefore( int(agent["end_before"]) )

            if "start_after" in agent:
                ag.startAfter( int(agent["start_after"]) )

        elif agent_type == "boiler":
            ag =  Boiler(id_number, range(0, 96), port_number, simulation=True)

            if "initial_qty" in agent:
                ag.setQty( int(agent["initial_qty"]) )

            if "max_qty" in agent:
                ag.max_qty = int( agent["max_qty"] )

            if "target_qty" in agent:
                ag.target_qty = int( agent["target_qty"] )

            if "power_when_on" in agent:
                ag.power_when_on = int( agent["power_when_on"] )

            if "end_before" in agent:
                ag.endsBefore( int(agent["end_before"]) )

            if "start_after" in agent:
                ag.startAfter( int(agent["start_after"]) )

        elif agent_type == "battery":
            ag = Battery(id_number, range(0, 96), port_number, simulation=True)

            if "max_capacity" in agent:
                ag.max_capacity = int(agent["max_capacity"])

            if "charge" in agent:
                ag.charge = int( agent["charge"] )

            if "max_power" in agent:
                ag.setMaxPower(int( agent["max_power"] ))
        else:
            raise NameError( "Impossibile creare un agente per {}".format(str(agent["type"])) )

        if ag != None:
            agents.append( ag )
            port_number += 1
            id_number   += 1

    if "solar_panel_radiation" in desc:
        ag = SolarPanel(id_number, range(0, 96), port_number, simulation=True)

        ag.setRadiation( getattr(SolarPanelRadiation, str(desc['solar_panel_radiation']).upper()) )

        port_number += 1
        id_number += 1

        agents.append(ag)

        print("\tSolarPanel con radiazioni: {}".format(desc['solar_panel_radiation']))

    if "fixed_load_file" in desc:
        FixedLoad.readFixedLoad( desc['fixed_load_file'] )
        print("\tFile Fixed Load associato: {}".format( desc['fixed_load_file'] ))

    # Dopo aver creato tutti gli agenti, li metto in comunicazione uno con l'altro
    for a1 in agents:
        for a2 in agents:
            # Escludo se stesso
            if a1.id != a2.id:
                a1.addNewDiscoveredAgent( a2.id, "127.0.0.1", a2.port,
                                          isProducingPower = a2.isProducingPower,
                                          optimizableAgent = a2.optimizableAgent )

    # Imposto la root per l'albero
    rootID = 1
    for a in agents:
        if a.id == rootID:
            a.isRoot = True
            a.rootID = rootID
        else:
            a.isRoot = False
            a.rootID = rootID

    # Avvio tutti i processi necessari
    parent_pid = os.getpid()

    children = []

    # Avvio i processi figlio
    for a in agents:
        if parent_pid == os.getpid():
            childid = os.fork()
            children.append(childid)
            if childid == 0:
                a.start()

    start_time = timeit.default_timer()

    # Attendo che tutti i figli termino
    if parent_pid == os.getpid():
        for i in children:
            os.wait()

        # PERFORMANCE
        elapsed = timeit.default_timer() - start_time

        performace_string = "SYSTEM PERFORMANCE:"
        performace_string += "\n\tTime elapsed: {}".format(elapsed)

        print(performace_string)

    # Termino tutti i processi figli lasciando in vita solamente il padre
    if parent_pid != os.getpid():
        sys.exit(0)

    # Sposto tutti i file della simulazione all'interno di una apposita cartella
    day_output_folder = os.path.join(scenario_output_folder, "giorno_{}".format(day))

    try:
        os.mkdir(day_output_folder)
    except FileExistsError:
        pass

    for the_file in os.listdir(output_folder):
        file_path = os.path.join(output_folder, the_file)
        if os.path.isfile(file_path):
            new_path = os.path.join(day_output_folder, the_file)
            move(file_path, new_path)

    day_merged_output = os.path.join(day_output_folder, "merged_output.csv")

    final_output_dict = OrderedDict()
    for the_file in os.listdir(day_output_folder):
        file_path = os.path.join(day_output_folder, the_file)
        if os.path.isfile(file_path):
            ar = np.genfromtxt(file_path)
            nome_file = os.path.splitext(the_file)[0]
            final_output_dict[nome_file] = ar

    # Calcolo la spesa energetica finale ed il consumo totale netto
    spesa_energetica            = []
    consumo_totale_netto        = []
    solar_panel_used_power      = []
    battery_power_consumption   = np.zeros( const.kTIME_SLOTS )
    solar_panel_power           = np.zeros( const.kTIME_SLOTS )
    solar_panel_usage           = np.zeros(const.kTIME_SLOTS)

    for t in range(0, const.kTIME_SLOTS):
        power_at_t = 0

        arr_cost = np.array(final_output_dict["cost"])
        cost_at_t = arr_cost[t]

        for f in final_output_dict:
            # Considero solo i cicli degli elettrodomestici e niente altro per il calcolo della
            # spesa energetica totale
            if "cycle" in f:
                arr_cycle = np.array(final_output_dict[f])

                if "Battery" in f:
                    battery_power_consumption[t] = arr_cycle[t]
                    if battery_power_consumption[t] < 0:
                        power_at_t = power_at_t + battery_power_consumption[t]
                else:
                    power_at_t = power_at_t + arr_cycle[t]

                if "SolarPanel" in f:
                    solar_panel_power[t] = abs(arr_cycle[t])

        power_at_t = max(0, power_at_t)

        spesa_at_t = power_at_t * cost_at_t * const.kHOUR_TO_TIMESLOT_RELATION / 1000000

        spesa_energetica.append( spesa_at_t )
        consumo_totale_netto.append( power_at_t )

    for t in range(0, const.kTIME_SLOTS):
        solar_panel_usage[t] = power_at_t
        if battery_power_consumption[t] > 0:
            solar_panel_usage[t] = solar_panel_usage[t] + battery_power_consumption[t]

        solar_panel_usage[t] = -1 * min(solar_panel_usage[t], solar_panel_power[t])

    final_output_dict.move_to_end("cost")
    column_format = '%i,' * (len(final_output_dict) - 1)
    column_format = '{}%.2f'.format(column_format)

    final_output_dict["solar_panel_real_usage"] = np.array(solar_panel_usage)
    final_output_dict["consumo_totale_netto"]   = np.array(consumo_totale_netto)
    final_output_dict["spesa_energetica"]       = np.array(spesa_energetica)

    # Fromato delle colonne del file csv. L'ultima colonna, la spesa energetica, ha come formato un float con 4
    # cifre deciamli dopo la virgola. Tutte le altre colonne sono interi

    column_format = '{},%i,%i,%.4f'.format(column_format)

    out_array = np.column_stack( list( final_output_dict.values() ))
    np.savetxt(day_merged_output, out_array, fmt=column_format, delimiter=',', header=",".join(final_output_dict.keys()), comments=" ")

printTitle( "Fine simulazione {}".format(nome_scenario) )