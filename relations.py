import cost
import numpy as np
import constants as consts

def createAllRelationForAgent(agent):
    relations = []
    for agent2 in [ agent.p ] + agent.pp:
        relations.append( getRelationBetween(agent, agent.otherAgents[ agent2 ]) )
        # Mi salvo la relazione con il padre, mi servirà dopo durante
        # la fase di VALUE propagation
        if agent2 == agent.p:
            agent.relationWithParent = relations[-1]

    return relations

"""
Crea una matrice con il valore di ogni assegnazione possibile per i due agenti
della varibile di inizio
@return {   'dim1' : int id dell'agente che è sulle righe,
            'dim2' : int id dell'agente che è sulle colonne,
            'rel' : np.matrix la matrice che contiene la relazione effettiva }
"""
def getRelationBetween(agent1, agent2):
    rel = np.zeros( shape = (consts.kTIME_SLOTS, consts.kTIME_SLOTS) )

    for t1 in range(0, consts.kTIME_SLOTS):
        for t2 in range(0, consts.kTIME_SLOTS):
            result = valueOfAssignmentPerAgents(t1, t2, agent1, agent2)
            rel[t1][t2] = result['cost']

    return { 'dim1' : agent1.id,
             'dim2' : agent2.id,
             'rel' : rel }

"""
Funzione EURISTICA che calcola il costo che avrebbe far iniziare
il ciclo degli agenti 1 e 2 rispettivamente negli istanti di tempo x1 ed x2
Più i valori sono bassi, meglio è
@return dict {  'status' : True|False a seconda se la soluzione è fattibile oppure no,
                'cost'   : float costo totale della soluzione}
"""
def valueOfAssignmentPerAgents(x1, x2, agent1, agent2):
    assignment_agent1 = agent1.getVarsFromStartingPoint(x1)
    assignment_agent2 = agent2.getVarsFromStartingPoint(x2)

    # Controllo che l'assegnazione sia valida per entrambi gli agenti
    if not assignment_agent1['status'] or not assignment_agent2['status']:
        return { 'status'   : False,
                 'cost'     : consts.kMAX_VALUE }

    used_power = np.array( assignment_agent1['vars'] + assignment_agent2['vars'] )

    # Controllo che il vincolo dei 3kW non venga superato
    # con l'assegnazione corrente
    for instant_power in used_power:
        if instant_power > consts.kMAX_POWER:
            return { 'status' : False,
                     'cost'   : consts.kMAX_VALUE }

    # Sottraggo l'energia prodotta dal pannello solare, se il pannello produce
    # più di quanto viene consumato, allora il valore diventa 0
    _tmp_solar_panel = [0] * consts.kTIME_SLOTS
    _tmp_sp_power = [10, 0, 3, 4, 20, 7, 4, 3, 9, 12, 30]
    _tmp_solar_panel[20:20+len(_tmp_sp_power)] = _tmp_sp_power

    solar_panel = np.array( _tmp_solar_panel )

    used_power_minus_sp = np.array( used_power - solar_panel )

    # Se la potenza usata è negativa, metto 0
    used_power_minus_sp[ np.where( used_power_minus_sp < 0) ] = 0

    # Calcolo il costo per ogni time-slot moltiplicando l'effettiva potenza utilizzata
    # per il costo di quel time-slot
    total_cost_per_time_slot = np.multiply(used_power_minus_sp, cost.getCostsArray())

    # Sommo il costo totale della mia soluzione, questo sarà il valore effettivo
    # della mia scelta
    total_cost = np.sum( total_cost_per_time_slot )

    return { 'status'   : True,
             'cost'     : total_cost }
