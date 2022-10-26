import sys, os, time
from typing import Callable, Optional, Set, List, Union
import networkx as nx

def get_neighbours(g: nx.Graph, node: int) -> Set[int]:
    return {int(node) for node in g.adj[node].keys()}
    
def filter_nodes(g: nx.Graph, key: str, value: Union[str, int], criterion: Callable) -> Set[int]:
    return {node for node in g.nodes if criterion(g.nodes[node][key],value)}

def get_domining_neighbours(g: nx.Graph, node: int) -> Set[int]:
    return {neighbour for neighbour in get_neighbours(g, node) if g.nodes[neighbour]['dominant']!=0}

def is_covered(g: nx.Graph, node: int) -> bool:
    covered=False
    if g.nodes[node]['dominant']==True:
        covered=True
    else:
        for neighbour in get_neighbours(g, node):
            if g.nodes[neighbour]['dominant']==True:
                covered=True
                break
    return covered

def get_path(tree: nx.DiGraph, node: int) -> List[int]:
    path = [node]
    while has_predecessors(tree, node):
        node = next(tree.predecessors(node))
        path.append(node)
    return path

def greedy_graph(g: nx.Graph) -> nx.Graph:
    domi_graph = nx.Graph()
    i=1
    while len(domi_graph.nodes) < len(g.nodes) :
        nodes_to_add=set()
        for node in set(g.nodes).difference(domi_graph.nodes):
            new_max = get_neighbours(g, str(node)).difference(domi_graph.nodes)
            if len(new_max) >= len(nodes_to_add):
                nodes_to_add = new_max
                domi_node=int(node)
        domi_graph.add_edges_from( [ ( domi_node, nd) for nd in nodes_to_add] )
        domi_graph.nodes[domi_node]['dominant']=i
        i+=1
        for nd in nodes_to_add:
            domi_graph.nodes[nd]['dominant']=0
    print(f"Domi node before purge: {filter_nodes(domi_graph, 'dominant', 0, lambda x,y : x!=y)}")
    return domi_graph

def semi_private_neighbours(g: nx.Graph, cluster: nx.DiGraph) -> Set[int]:
    set_semi_private = set()
    for node in g.nodes:
        if g.nodes[node]['dominant']!=0:
            if node in cluster.nodes:
                if cluster.nodes[node]['state']=='purified':
                    continue
        else:
            pass
        if len(get_domining_neighbours(g,node).intersection(
            filter_nodes(cluster, 'state', 'purified', lambda x,y : x!=y)))<=1:
            set_semi_private.add(node)
    return set_semi_private

def alone_nodes(g: nx.Graph, cluster: nx.DiGraph) -> Set[int]:
    set_semi_private = set()
    for node in g.nodes:
        print(node)
        if g.nodes[node]['dominant']!=0:
            print('dominant')
            if node in cluster.nodes:
                if cluster.nodes[node]['state']=='purified':
                    print('purified')
                    pass
            else:
                continue
        if len(get_domining_neighbours(g,node).intersection(
            filter_nodes(cluster, 'state', 'purified', lambda x,y : x!=y)))==0:
            print('added')
            set_semi_private.add(node)
    return set_semi_private
    
def get_highest_firm(cluster: nx.DiGraph, tree: nx.DiGraph, leaves: List[int], pending_nodes: List[int]) -> Optional[int]:
    highest_firm: Optional[int] = None
    highest_level=-1
    for leaf in leaves:
        node = leaf
        firm: Optional[int] = None
        level=-1
        while not firm:
            if not has_predecessors(tree, node):
                break
            if next(tree.predecessors(node)) in pending_nodes:
                if cluster.nodes[node]['state']=='firm':
                    firm = node
                    level+=1
            node = next(tree.predecessors(node))
        if highest_level<level:
            highest_firm = firm
    return highest_firm

def build_forest(g: nx.Graph):
    cluster = nx.DiGraph()
    dominings = sorted(filter_nodes(g, 'dominant', 0, lambda x,y : x!=y),
        key= lambda node: g.nodes[node]['dominant'])
    for node in dominings:
        neighbours = get_neighbours(g, node).intersection(set(dominings))
        for neighbour in neighbours:
            if neighbour not in cluster.nodes:
                cluster.add_edge(node, neighbour)
    return cluster

def has_successors(di_g: nx.DiGraph, node: int):
    try:
        next(di_g.successors(node))
        return True
    except StopIteration:
        return False


def has_predecessors(di_g: nx.DiGraph, node: int):
    try:
        next(di_g.predecessors(node))
        return True
    except StopIteration:
        return False

def purify_tree(g: nx.Graph, cluster: nx.DiGraph, tree: nx.DiGraph):
    print(f"The tree is {tree.nodes}")
    leaves = [node for node in tree.nodes if not has_successors(tree, node)]
    pending_nodes = set(tree.nodes)
    for node in leaves:
        if get_neighbours(g, node).intersection(set(semi_private_neighbours(g, cluster)))!=set():
            print(f"Node {node} will be set as firm")
            cluster.nodes[node]['state']='firm'
            pending_nodes = pending_nodes.difference({node})
        else:
            print(f"Node {node} will be set as purified")
            cluster.nodes[node]['state']='purified'
            cluster.nodes[next(cluster.predecessors(node))]['state']='firm'
            pending_nodes = pending_nodes.difference({node, next(cluster.predecessors(node))})
    print("Leaves phase finished")
    while len(pending_nodes)!=0:
        print(pending_nodes)
        for node in pending_nodes: 
            if node in semi_private_neighbours(g, cluster).intersection({node}):
                print(f"Node {node} will be set as firm in pre-step")
                cluster.nodes[node]['state']='firm'
        highest_firm = get_highest_firm(cluster, tree, leaves, pending_nodes)
        if not highest_firm:
            return cluster
        else:
            path = get_path(tree, highest_firm)
            if len(path)<=2 or cluster.nodes[path[1]]['state']!='pending':
                return cluster
            elif len(path)==3 or cluster.nodes[path[2]]['state']!='pending':
                print(f"Is it purified : {path[1] in semi_private_neighbours(g, cluster).intersection({path[1]})}")
                set_l = {node for node in g.nodes if len(alone_nodes(g,cluster))==0}
                print(f"Nodes that are alone : {set_l}")
                cluster.nodes[path[1]]['state']='purified'
                print(f"Node {path[1]} will be set as purified in step")
            else:
                cluster.nodes[path[1]]['state']='purified'
                cluster.nodes[path[2]]['state']='purified'
                print(f"Node {path[1]} will be set as purified in step")
                print(f"Node {path[2]} will be set as purified in step")
        pending_nodes=filter_nodes(cluster, 'state', 'pending', lambda x,y : x==y).intersection(tree.nodes)
    return cluster

def purify_graph(g: nx.Graph) -> nx.Graph:
    cluster = build_forest(g)
    temp_graph = cluster.to_undirected()
    for node in cluster.nodes:
        cluster.nodes[node]['state']='pending'
    trees = [cluster.subgraph(c).copy() for c in nx.connected_components(temp_graph)]
    for tree in trees: 
        cluster=purify_tree(g, cluster, tree)
    purified_nodes=filter_nodes(cluster, 'state', 'purified', lambda x,y : x==y)
    print(f"Alone nodes : {alone_nodes(g, cluster)}")
    for node in purified_nodes:
        print('Purified')
        g.nodes[node]['dominant']=0
    return g
                
def dominant(g: nx.Graph):
    """
        A Faire:         
        - Ecrire une fonction qui retourne le dominant du graphe non dirigé g passé en parametre.
        - cette fonction doit retourner la liste des noeuds d'un petit dominant de g

        :param g: le graphe est donné dans le format networkx : https://networkx.github.io/documentation/stable/reference/classes/graph.html

    """
    domi_graph = greedy_graph(g)
    purified_graph = purify_graph(domi_graph)
    list_domining = filter_nodes(purified_graph, 'dominant', 0, lambda x,y: x!=y)
    for node in purified_graph.nodes:
        if len((get_neighbours(purified_graph, node).union({node})).intersection(list_domining))==0:
            print(f"{node} Not Domining!")
    return [node for node in domi_graph.nodes if purified_graph.nodes[node]['dominant']]



#########################################
#### Ne pas modifier le code suivant ####
#########################################
if __name__=="__main__":
    input_dir = os.path.abspath(sys.argv[1])
    output_dir = os.path.abspath(sys.argv[2])
    
    # un repertoire des graphes en entree doit être passé en parametre 1
    if not os.path.isdir(input_dir):
	    print(input_dir, "doesn't exist")
	    exit()

    # un repertoire pour enregistrer les dominants doit être passé en parametre 2
    if not os.path.isdir(output_dir):
	    print(input_dir, "doesn't exist")
	    exit()       
	
    # fichier des reponses depose dans le output_dir et annote par date/heure
    output_filename = 'answers_{}.txt'.format(time.strftime("%d%b%Y_%H%M%S", time.localtime()))             
    output_file = open(os.path.join(output_dir, output_filename), 'w')
    score = 0

    for graph_filename in sorted(os.listdir(input_dir)):
        #print(graph_filename)
        # importer le graphe
        g = nx.read_adjlist(os.path.join(input_dir, graph_filename))
        
        # calcul du dominant
        D = sorted(dominant(g), key=lambda x: int(x))

        # ajout au rapport
        output_file.write(graph_filename)
        for node in D:
            output_file.write(' {}'.format(node))
            score+=1
        output_file.write('\n')
    print(score)
        
    output_file.close()
