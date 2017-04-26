import time
import numpy as np
from message import MessageType as msgType
import relations
import constants as consts

def start( agent ):
    agent.debug("Starting UTIL Message propagation...")

    if agent.isLeaf():
        agent.debug("Sono una foglia")

        # Ottengo una lista con tutte le relazioni per quell'agente
        rels_raw = relations.createAllRelationForAgent( agent )

        # Per ognuna delle relazioni trovate al passo precedente faccio la proiezione
        # sull'agente attuale
        rels = []
        for r in rels_raw:
            rels.append( projectionOfAgentOnRelation(agent.id, r) )

        # Invio tutte le relazioni al mio genitore
        agent.sendMsg(agent.p, msgType.UTIL, rels)

    else:
        agent.debug("Non foglia")

        # Attendo che arrivino tutti i messaggi dai figli (solamente children, NON pseudo-children)
        while True:
            all_children_msgs_arrived = True
            time.sleep(0.5)
            for id in agent.c:
                if ( (int(id), str(msgType.UTIL)) ) not in agent.msgs:
                    all_children_msgs_arrived = False
                    break

            if all_children_msgs_arrived == True:
                break

        if agent.isRoot:
            agent.debug("Sono la ROOT, da me partira' la VALUE Propagation")
            agent.debug(agent.msgs)
            return

        # Proseguo nel caso in cui l'agente non sia root

        # Crea le relazioni con i suoi genitori
        rels_raw = relations.createAllRelationForAgent(agent)

        # Salvo in received_utils tutti i valori dei messaggi di UTIL
        received_utils = {}
        for msg_key in agent.msgs:
            #sender_id   = msg_key[0]
            msg_type    = msg_key[1]
            msg         = agent.msgs[ msg_key ]
            if msg_type == msgType.UTIL:
                rel = msg.value
                if int(rel['dim2']) in received_utils:
                    received_utils[ int(rel['dim2']) ] = received_utils[int(rel['dim2'])] + np.array(rel['rel'])
                else:
                    received_utils[ int(rel['dim2']) ] = np.array( rel['rel'] )

        for idx, rel in enumerate(rels_raw):
            if int(rel['dim1']) in received_utils:
                # Sommo lungo le righe
                a = received_utils[ int(rel['dim1']) ]
                b = a.reshape(1, len(a))
                rels_raw[idx] = np.add(rels_raw[idx], b.T)

            if int(rel['dim2']) in received_utils:
                # Sommo lungo le colonne
                rels_raw[idx] = np.add(rels_raw[idx], received_utils[ int(rel['dim2']) ])

        # Ora non mi resta che sommare ad ognuna delle relazioni di questo agente i valori
        # presenti in cumulative_util, per poi proiettare ed inviare
        rels = []
        for r in rels_raw:
            rels.append( projectionOfAgentOnRelation(agent.id, r) )

        agent.sendMsg(agent.p, msgType.UTIL, rels)

def projectionOfAgentOnRelation(id, rel):

    return { 'dim1': rel['dim1'],
             'dim2': rel['dim2'],
             'rel' : np.amax(rel, axis = 0) }