import time
from message import MessageType as msgType
from message import Message as message
import dfsPseudotree as dfs

def start( agent ):
    agent.debug("Starting pseudotree_creation...")

    # Attendo finche' l'agente non e' disponibile per ascoltare
    # i messaggi in arrivo
    while ( not agent.isListening ):
        time.sleep(0.5)

    agent.debug("Ready to start pseudotree creation")

    """
    NODO ROOT
    Avvio la procedura nel caso di nodo root
    """
    if agent.isRoot:
        # Attendo che tutti i miei vicini mi mandino la lista
        # dei loro vicini
        while True:
            all_neighbor_msgs_arrived = True
            time.sleep(0.5)
            for id in agent.otherAgents:
                if ( (int(id), str(msgType.NEIGHBORS)) ) not in agent.msgs:
                    all_neighbor_msgs_arrived = False
                    break

            if all_neighbor_msgs_arrived == True:
                break

        # Ora ho ricevuto tutti i messaggi dai miei vicini che a loro volta
        # contengono i loro vicini. Ogni agente e' identificato con un ID numerico
        # intero.

        # Inizio il grafo avendo come elemento di inizio la lista dei vicini della ROOT
        graph = {}
        graph[ agent.id ] = [ a for a in agent.otherAgents ]

        # Aggiungo in una lista mano a mano tutti i miei vicini
        for msg_key in agent.msgs:
            sender_id   = msg_key[0]
            msg_type    = msg_key[1]
            msg         = agent.msgs[ msg_key ]
            if msg_type == msgType.NEIGHBORS:
                graph[ int(sender_id) ] = list( msg.value )

        # Creo lo pseudoalbero con la procedura DFS
        pseudotree = dfs.dfs(graph, agent.id)

        # Recupero i dati su parents, pseudo_parents e pseudo_children
        parents, pseudo_parent, pseudo_children = dfs.getRelatives(graph, pseudotree)

        # Mi assegno i valori di p, pp, pc e c
        agent.p     = parents[agent.id]
        agent.pp    = pseudo_parent[agent.id]
        agent.pc    = pseudo_children[agent.id]
        agent.c     = pseudotree[agent.id]

        # Invio a tutti gli altri nodi i rispettivi valori di p, pp, c e pc
        for node in graph:
            if node is not agent.id:
                agent.sendMsg(node, msgType.PTINFO, (parents[node], pseudo_parent[node], pseudotree[node], pseudo_children[node]) )

        # A tutti i miei sottoposti, sia reali sia pseudo, invio il mio dominio
        for child in agent.c + agent.pc:
            agent.sendMsg(child, msgType.DOMAIN, agent.domain)

    else:
        """
        NODO GENERICO NON ROOT
        """

        # Invio i miei vicini alla root
        agent.sendMsg(agent.rootID, msgType.NEIGHBORS, agent.otherAgents)

        # Attendo che la root mi restituisca le PTINFO
        key_msg_ptinfo = (int(agent.rootID), str(msgType.PTINFO))

        while key_msg_ptinfo not in agent.msgs:
            time.sleep(0.5)
            pass

        msg_ptinfo = agent.msgs[ key_msg_ptinfo ]
        agent.p, agent.pp, agent.c, agent.pc = msg_ptinfo.value

        # A tutti i miei sottoposti, sia reali sia pseudo, invio il mio dominio
        for child in agent.c + agent.pc:
            agent.sendMsg(child, msgType.DOMAIN, agent.domain)

        # Aspetto che mi arrivi il dominio da tutti i miei parent e pseudo_parents
        while True:
            all_parents_msgs_arrived = True
            time.sleep(0.5)

            for parent in [agent.p] + agent.pp:
                if ( (int(parent), str(msgType.DOMAIN)) ) not in agent.msgs:
                    all_parents_msgs_arrived = False
                    break

            if all_parents_msgs_arrived == True:
                break

        # Assegno ad ogni nodo il suo dominio dopo che ho ricevuto il messaggio
        for parent in [agent.p] + agent.pp:
            agent.otherAgents[parent].domain = agent.msgs[ (int(parent), str(msgType.DOMAIN)) ]

    agent.debug("End of pseudotree creation.")