def dfs(graph, start):
    tree    = {}
    visited = set()

    tree = visit(graph, start, 'root', tree, visited)

    for node in graph:
        if node not in tree:
            tree[ node ] = []

    return tree

def visit(graph, node, parent, tree, visited):

    if node not in visited:
        if parent in tree:
            tree[parent].append( node )
        else:
            tree[parent] = [ node ]

        visited.add(node)

        for child in graph[node]:
            visit(graph, child, node, tree, visited )

    return tree

def getParentFromPseudotree(pseudotree):
    parents = {}

    for node_id, children in pseudotree.items():
        for child in children:
            parents[child] = node_id

    return parents

def assignDepthFromPseudotree(pseudotree):
    depths = {}
    start = pseudotree['root'][0]
    depths = assignDepth(pseudotree, start, depths, -1)

    return depths

def assignDepth(tree, node, depths, curr_depth):
    depths[ node ] = curr_depth + 1;
    for child in tree[ node ]:
        assignDepth(tree, child, depths, curr_depth + 1)
    return depths

def getRelatives(graph, pseudotree):
    parents         = getParentFromPseudotree(pseudotree)
    pseudo_children = {}
    pseudo_parent   = {}

    depths = assignDepthFromPseudotree(pseudotree)

    for node_id in pseudotree:

        # Se sto vagliando la root, salto perche' non mi interessa
        # essendo un nodo fittizio
        if node_id == 'root':
            continue

        # I genitori li prendo dalla struttura dati apposita
        p = parents[node_id]

        # I figli di ogni nodo si possono recuperare direttamente
        # dell'albero
        c = pseudotree[node_id]

        # Pseudo-parents
        pp = []

        # Pseudo-children
        pc = []

        pseudo_relatives = list( set( graph[node_id] ) - set( [p] ) - set( c ) )

        for relative in pseudo_relatives:
            if depths[node_id] < depths[relative]:
                pc.append(relative)
            else:
                pp.append(relative)

        pseudo_parent[node_id]      = pp
        pseudo_children[node_id]    = pc

    return (parents, pseudo_parent, pseudo_children)