from agent import Agent
import constants as consts
import numpy as np
from message import MessageType as msgType
import time
import os

class Battery(Agent):
    def __init__(self, id, addr, port, simulation = False):
        super().__init__(id, addr, port, simulation)
        self.name = "Battery"

        self.cycle = np.zeros( consts.kTIME_SLOTS )

        self.max_capacity   = 2000 #Wh
        self.charge         = 1500 #Wh

        # Potenza massima di carica/scarica
        self.max_power      = 2000 #W

        self.maxDischargeIstantaneous   = self.max_power * consts.kHOUR_TO_TIMESLOT_RELATION
        self.maxRechargeIstantaneous    = self.max_power * consts.kHOUR_TO_TIMESLOT_RELATION

        self.optimizableAgent = False

    """
    Funzioni essenzali per un agente
    """
    def getCycle(self):
        return self.cycle

    def getVarsFromStartingPoint(self, x):
        return {    'status'    : True,
                    'vars'      : np.array(self.cycle) }

    def getAvailPowerFromStartingPoint(self, x, other_agent):
        return {    'status'    : True,
                    'vars'      : np.array(self.cycle) }

    """
    Funzioni batteria
    """
    def getPowerFromConsumption(self, c):
        if self.charge <= 0:
            return 0

        return min(self.charge, min(c, self.maxDischargeIstantaneous))

    def getPowerFromRecharge(self, sp):
        if self.charge >= self.max_capacity:
            return 0

        delta = self.max_capacity - self.charge

        return min(sp, min(self.maxRechargeIstantaneous, delta))

    # Sono un agente non ottimizzabile, attendo la fine della procedura di ottimizzazione per
    # determinare il mio ciclo con carica e scarica.
    def waitOptimizationEnd(self):
        self.debug("Operazioni post ottimizzazione")

        # Attendo il ciclo di tutti gli altri agenti coinvolti
        start_time = time.time()
        while True:
            all_other_agents_cycle_msg_arrived = True
            time.sleep(0.5)
            for id in self.otherAgents:
                if ( (int(id), str(msgType.FINAL_CYCLE)) ) not in self.msgs:
                    all_other_agents_cycle_msg_arrived = False
                    break

            if all_other_agents_cycle_msg_arrived == True:
                break

            # Se trascorro più di 10 secondi bloccato, esco ed attendo la prossima
            # ottimizzazione
            elapsed_time = time.time() - start_time
            if elapsed_time > 10:
                return False

        charge_value    = []
        charge_perc     = []

        solar_panel_cycle = []
        others_cycles = {}
        for msg_key in self.msgs:
            sender_id   = msg_key[0]
            msg_type    = msg_key[1]
            msg = self.msgs[msg_key]
            if msg_type == msgType.FINAL_CYCLE:
                if self.otherAgents[sender_id].isProducingPower:
                    solar_panel_cycle = msg.value
                else:
                    others_cycles[sender_id] = msg.value

        # Calcolo il mio ciclo: dove gli altri agenti usano potenza io mi scarico di una determinata
        # quantità massimo, altrimenti mi carico con l'energia del pannello solare

        avail_power     = np.zeros( consts.kTIME_SLOTS )
        finale_cycle    = np.zeros( consts.kTIME_SLOTS )
        for t in range(0, consts.kTIME_SLOTS):
            current_cycle = solar_panel_cycle[t]
            for id in others_cycles:
                current_cycle += others_cycles[id][t]

            current_cycle   = max(0, current_cycle)
            avail_power[t]  = max(0, abs(solar_panel_cycle[t]) - current_cycle)

            if current_cycle > 0:
                finale_cycle[t] = -1 * self.getPowerFromConsumption( current_cycle )
            else:
                finale_cycle[t] = self.getPowerFromRecharge( avail_power[t] )

            self.charge = self.charge + (finale_cycle[t] * consts.kHOUR_TO_TIMESLOT_RELATION)

            charge_value.append( self.charge )
            charge_perc.append( self.charge / self.max_capacity * 100 )

        self.saveFinalCycle( finale_cycle )

        # La batteria salva anche altre informazioni oltre al proprio ciclo, come il livello di carica
        # ad ogni time-step, sia in valori assoluti che in percentuale
        dir = os.path.dirname(__file__)
        output_folder = os.path.join(dir, "output")

        charge_value_filename_path  = os.path.join(output_folder, '{}_{}_charge_value.csv'.format(self.name, self.id))
        charge_perc_filename_path   = os.path.join(output_folder, '{}_{}_charge_perc.csv'.format(self.name, self.id))

        np.savetxt(charge_value_filename_path,  np.array(charge_value), fmt='%i', delimiter=',')
        np.savetxt(charge_perc_filename_path,   np.array(charge_perc), fmt='%i', delimiter=',')