import time
import numpy as np
from message import MessageType as msgType
import relations
import constants as consts

def start( agent ):
    agent.debug("Starting UTIL Message propagation...")

    if agent.isLeaf():
        #agent.debug("Sono una foglia")

        # Ottengo una lista con tutte le relazioni per quell'agente
        rels_raw = relations.createAllRelationForAgent( agent )

        # Per ognuna delle relazioni trovate al passo precedente faccio la proiezione
        # sull'agente attuale
        rels = []
        for r in rels_raw:
            rels.append( projectionOfAgentOnRelation(agent.id, r) )

        # Invio tutte le relazioni al mio genitore
        agent.sendMsg(agent.p, msgType.UTIL, rels)

        # Invio informazioni al padre su tutti gli agenti che producono energia
        producing_energy_msg = {}
        for id in agent.otherAgents:
            a = agent.otherAgents[id]
            if a.isProducingPower:
                # print([ a.otherAgentsInfluence[ag_id].id for ag_id in a.otherAgentsInfluence ])
                producing_energy_msg[a.id] = [a.otherAgentsInfluence[ag_id].id for ag_id in a.otherAgentsInfluence]

        if len(producing_energy_msg) > 0:
            agent.sendMsg(agent.p, msgType.PROD_ENERGY_CONSIDERED_AGENT, producing_energy_msg)

        # Nel caso in cui sia io l'agente che produce energia, invio le mie informazioni
        producing_energy_msg = {}
        if agent.isProducingPower:
            # print([agent.otherAgentsInfluence[ag_id].id for ag_id in agent.otherAgentsInfluence])
            # agent.debug("Produco quindi mando")
            producing_energy_msg[agent.id] = [agent.otherAgentsInfluence[ag_id].id for ag_id in agent.otherAgentsInfluence]
            agent.sendMsg(agent.p, msgType.PROD_ENERGY_CONSIDERED_AGENT, producing_energy_msg)

    else:
        #agent.debug("Non foglia")

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

        # Attendo che i messaggi con gli agenti già considerati per tutti gli agenti
        # che producono potenza
        while True:
            all_children_msgs_arrived = True
            time.sleep(0.5)
            agent.debug("Attendo informazioni su chi produce")
            #agent.debug(agent.msgs)
            for id in agent.c:
                if ((int(id), str(msgType.PROD_ENERGY_CONSIDERED_AGENT))) not in agent.msgs:
                    all_children_msgs_arrived = False
                    break
            if all_children_msgs_arrived == True:
                break

        for msg_key in agent.msgs:
            #sender_id   = msg_key[0]
            msg_type    = msg_key[1]
            msg         = agent.msgs[ msg_key ]
            if msg_type == msgType.PROD_ENERGY_CONSIDERED_AGENT:
                # Salvo la lista inviata
                producing_energy_msg_value = msg.value

                # Per ogni agente controllo se produce potenza, nel caso, se il suo id è nella lista,
                # prendo gli agenti che ha già considerato
                for id in agent.otherAgents:
                    a = agent.otherAgents[id]
                    if a.isProducingPower:
                        if a.id in producing_energy_msg_value:
                            for id in producing_energy_msg_value[a.id]:
                                if id in agent.otherAgents:
                                    a.otherAgentsInfluence[id] = agent.otherAgents[id]

        if agent.isRoot:
            root_util = None
            for msg_key in agent.msgs:
                # sender_id   = msg_key[0]
                msg_type = msg_key[1]
                msg = agent.msgs[msg_key]
                if msg_type == msgType.UTIL:
                    # msg.value[0] e NON msg.value perché la ROOT nel nostro caso riceve
                    # solamente l'utility dal suo unico figlio
                    root_util = msg.value[0]

            # Cerco dove l'utility è minima per l'agente ROOT
            agent.value = np.argmin( np.array( root_util['rel'] ) )

            for child in agent.c:
                agent.sendMsg(child, msgType.VALUE, agent.value)

            agent.debug("Inizio al time-step: {}".format(agent.value))
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
                for rel in msg.value:
                    if int(rel['dim2']) in received_utils:
                        received_utils[ int(rel['dim2']) ] = received_utils[int(rel['dim2'])] + np.array(rel['rel'])
                    else:
                        received_utils[ int(rel['dim2']) ] = np.array( rel['rel'] )

        for idx, rel in enumerate(rels_raw):
            if int(rel['dim1']) in received_utils:
                # Sommo lungo le righe
                a = received_utils[ int(rel['dim1']) ]
                b = a.reshape(1, len(a))
                rels_raw[idx]['rel'] = np.add( rels_raw[idx]['rel'], b.T)

            if int(rel['dim2']) in received_utils:
                # Sommo lungo le colonne
                rels_raw[idx]['rel'] = np.add( rels_raw[idx]['rel'], received_utils[ int(rel['dim2']) ])

        # Ora non mi resta che sommare ad ognuna delle relazioni di questo agente i valori
        # presenti in cumulative_util, per poi proiettare ed inviare
        rels = []
        for r in rels_raw:
            rels.append( projectionOfAgentOnRelation(agent.id, r) )

        agent.sendMsg(agent.p, msgType.UTIL, rels)

        # Invio informazioni al padre su tutti gli agenti che producono energia
        producing_energy_msg = {}
        for id in agent.otherAgents:
            a = agent.otherAgents[id]
            if a.isProducingPower:
                # print([ a.otherAgentsInfluence[ag_id].id for ag_id in a.otherAgentsInfluence ])
                producing_energy_msg[a.id] = [a.otherAgentsInfluence[ag_id].id for ag_id in a.otherAgentsInfluence]

        if len(producing_energy_msg) > 0:
            agent.sendMsg(agent.p, msgType.PROD_ENERGY_CONSIDERED_AGENT, producing_energy_msg)

        # Nel caso in cui sia io l'agente che produce energia, invio le mie informazioni
        producing_energy_msg = {}
        if agent.isProducingPower:
            # print([agent.otherAgentsInfluence[ag_id].id for ag_id in agent.otherAgentsInfluence])
            # agent.debug("Produco quindi mando")
            producing_energy_msg[agent.id] = [agent.otherAgentsInfluence[ag_id].id for ag_id in
                                              agent.otherAgentsInfluence]
            agent.sendMsg(agent.p, msgType.PROD_ENERGY_CONSIDERED_AGENT, producing_energy_msg)

def projectionOfAgentOnRelation(id, rel):

    return { 'dim1': rel['dim1'],
             'dim2': rel['dim2'],
             'rel' : np.amin(rel['rel'], axis = 0) } #np.amax(rel['rel'], axis = 0)