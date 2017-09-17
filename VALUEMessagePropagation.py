import time
import numpy as np
import constants as consts
from message import MessageType as msgType

def start(agent):
    if agent.killStartThread:
        return False

    parent_value = None

    while True:
        if agent.killStartThread:
            return False

        util_msg_recieved = False
        for msg_key in agent.msgs:
            # sender_id   = msg_key[0]
            msg_type = msg_key[1]
            msg = agent.msgs[msg_key]
            if msg_type == msgType.VALUE:
                parent_value = msg.value
                util_msg_recieved = True
                break
        if util_msg_recieved:
            break
        time.sleep(0.5)

    rel = agent.relationWithParent['rel']

    parent_selected_column = rel[:,parent_value]

    # Cerco dove è il minimo lungo le colonne. Il mio valore sarà il valore corrispondente
    # alla casella di quello selezionato dal padre.
    # Esempio: parent_value = 2
    # rel:  [[10,  2, 33],
    #        [ 4, 54,  6],
    #        [87,  8,  9]]
    # np.argmin(rel, axis=1) -> array([1, 0, 1])
    # Il mio valore è quello in posizione 2 (parent_value) dell'array
    # che corrisponde al valore 6 della matrice

    # Controllo che con i vincoli imposti si possa fare
    # #agent_col = np.argmin(rel, axis=1)
    #
    # mask_inf = np.isinf( agent_col )
    # sum_inf = np.sum( mask_inf )
    # agent.debug(rel)
    # agent.debug(agent_col)
    # agent.debug(sum_inf)

    # if sum_inf == len(rel):
    #     agent.debug("[ERRORE] Impossibile rispettare i vincoli")
    #     agent.value = 0
    # else:
    #     agent.value = agent_col[ parent_value ]

    sum_inf = 0
    for e in parent_selected_column:
        if e == consts.kMAX_VALUE:
            sum_inf += 1
    #agent.debug(parent_selected_column)
    if sum_inf == len(parent_selected_column):
        agent.debug("[ERRORE] Impossibile rispettare i vincoli")
        agent.value = 0
    else:
        agent.value = np.argmin(parent_selected_column)

    for child in agent.c:
        agent.sendMsg(child, msgType.VALUE, agent.value)

    agent.debug("Inizio al time-step: {}".format(agent.value))
