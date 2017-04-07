import time
from message import MessageType as msgType
from message import Message as msg
import pseudotree
import collections

Relatives = collections.namedtuple('Relatives', 'parent pseudoparents children pseudochildren')

def bfs(tree, tree_node, procedure, *extra_procedure_args):
    """"
    Run a the 'procedure' recursively, in a breadth-first-search way, starting
    from the 'tree_node' in the 'tree'.
    """

    # print extra_procedure_args
    # agent, graph, parents, pstree, depths = extra_procedure_args
    procedure(tree_node, *extra_procedure_args)
    for child in tree[tree_node]:
        bfs(tree, child, procedure, *extra_procedure_args)

def tell_relative(node_id, agent, graph, parents, pstree, depths):
    """
    Send a UDP message titled 'ptinfo', which tells the agent with 'node_id'
    its (p, pp, c, pc). Only the root is supposed to call this procedure.
    Hence, if the 'node_id' is of the root itself, it simply sets the
    appropriate fields.
    """

    # Only the root calls this function
    assert agent.isRoot == True

    p = parents[node_id]
    c = pstree[node_id]
    pp = []
    pc = []
    pseudo_relatives = set(graph[node_id]) - set([p]) - set(c)
    pseudo_relatives = list(pseudo_relatives)
    for relative in pseudo_relatives:
        if depths[node_id] < depths[relative]:
            pc.append(relative)
        else:
            pp.append(relative)

    # Set appropriate the fields if node_id is same as root_id, or send the
    # 'ptinfo' message otherwise.
    if node_id == agent.rootID:
        agent.p, agent.pp, agent.c, agent.pc = p, pp, c, pc
    else:
        agent.sendMsg(node_id, msgType.PTINFO, msgType.PTINFO, Relatives(p, pp, c, pc) )

def pseudotreeCreation(agent):
    agent.debug('Start pseudotree_creation')

    # Attendo finche' l'agento non e' disponibile per ascoltare
    # i messaggi in arrivo
    while ( not agent.isListening ):
        time.sleep(0.5)
        agent.debug( str(agent.isListening) )

    agent.debug('Ready')

    # Procedura nel caso di ROOT
    if agent.isRoot:
        agent.debug('Root A')
        # Attendo finche' ogni agente non ha mandato la sua intera lista dei vicini
        while True:
            all_neighbor_msgs_arrived = True
            for id in agent.otherAgents:
                if ( msgType.NEIGHBORS + str( id ) ) not in agent.msgs:
                    all_neighbor_msgs_arrived = False
                    break
            if all_neighbor_msgs_arrived == True:
                break
        agent.debug('Root B')
        # Create the graph and use it to generate the pseudo-tree structure.
        graph = {}
        graph[ agent.id ] = [a for a in agent.otherAgents]

        for title, m in agent.msgs.items():
            if m.type == msgType.NEIGHBORS:
                graph[ int( m.sender ) ] = list( m.value )

        pstree = pseudotree.dfsTree(graph, agent.id)

        parents = pseudotree.get_parents(pstree)
        depths = pseudotree.assign_depths(pstree)
        bfs(    pstree,
                pstree['Nothing'][0],
                tell_relative,
                agent, graph, parents, pstree, depths
            )

        # Send this node's (root's) domain to all children and pseudochildren
        # For example, if root's id is 1, the message is, in title:value form:
        # domain_1: <the set which is the domain of 1>
        for child in agent.c + agent.pc:
            agent.sendMsg(child, msgType.DOMAIN, msgType.DOMAIN + str(agent.id), agent.domain)

    # Caso in cui NON sia ROOT
    else:
        agent.debug('NON Root A')
        otherAgentsId = [a for a in agent.otherAgents]
        agent.sendMsg(agent.rootID, msgType.NEIGHBORS, msgType.NEIGHBORS + str( agent.id ), otherAgentsId)

        # Wait till the message (p, pp, c, pc) [has title: 'ptinfo'] arrives
        # from the root.
        while msgType.PTINFO not in agent.msgs:
            time.sleep(0.5)
            pass

        agent.debug('NON Root B')

        # Initialize all the respective fields
        ptinfo_msg = agent.msgs[ msgType.PTINFO ]
        agent.p, agent.pp, agent.c, agent.pc = ptinfo_msg.value

        # Send this node's domain to all children and pseudochildren.
        # For example, if this node's id is 7, the message is, in title:value
        # form would be:
        # domain_7: <the set which is the domain of 7>
        for child in agent.c + agent.pc:
            agent.sendMsg(child, msgType.DOMAIN, msgType.DOMAIN + str(agent.id), agent.domain)

        while True:
            all_parents_msgs_arrived = True
            for parent in [agent.p] + agent.pp:
                if ( msgType.DOMAIN + str(parent) ) not in agent.msgs:
                    all_parents_msgs_arrived = False
                    break
            if all_parents_msgs_arrived == True:
                break

        for parent in [agent.p] + agent.pp:
            domain_msg = agent.msgs[msgType.DOMAIN + str(parent) ]
            agent.otherAgents[ parent ].domain = domain_msg.value

    print( str(agent.id) + ': End pseudotree_creation')