import time
import numpy as np
from message import MessageType as msgType

def start(agent):
    parent_value = None

    while True:
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

    # Cerco dove è il minimo lungo le colonne. Il mio valore sarà il valore corrispondente
    # alla casella di quello selezionato dal padre.
    # Esempio: parent_value = 2
    # rel:  [[10,  2, 33],
    #        [ 4, 54,  6],
    #        [87,  8,  9]]
    # np.argmin(rel, axis=1) -> array([1, 0, 1])
    # Il mio valore è quello in posizione 2 (parent_value) dell'array
    # che corrisponde al valore 6 della matrice

    agent_col = np.argmin(rel, axis = 1)
    agent.value = agent_col[ parent_value ]

    for child in agent.c:
        agent.sendMsg(child, msgType.VALUE, agent.value)

    agent.debug("Inizio al time-step: {}".format(agent.value))
