from statistics import mean
import sys, os, time
from typing import Set
import networkx as nx

def convert_graph_to_int(g: nx.Graph) -> nx.Graph:
    converted_graph = nx.Graph()
    for edge in g.edges:
        converted_graph.add_edge(int(edge[0]), int(edge[1]))
    return converted_graph

def get_neighbours(g: nx.Graph, node: int) -> Set[int]:
    return {node for node in g.adj[node].keys()}

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
    
def greedy_graph(g: nx.Graph, partly_domi: nx.Graph) -> nx.Graph:
    domi_graph = partly_domi
    while len(domi_graph.nodes) < len(g.nodes) :
        nodes_to_add=set()
        for node in set(g.nodes):
            new_max = get_neighbours(g, node).difference(domi_graph.nodes)
            if len(new_max) >= len(nodes_to_add):
                nodes_to_add = new_max
                domi_node=node
        domi_graph.add_edges_from( [ ( domi_node, nd) for nd in nodes_to_add] )
        domi_graph.nodes[domi_node]['dominant']=True
        for nd in nodes_to_add:
            domi_graph.nodes[nd]['dominant']=False
    return domi_graph

def purify_graph(g: nx.Graph) -> nx.Graph:
    inter_l = [node for node in g.nodes if g.nodes[node]['dominant']]
    for node in inter_l:
        g.nodes[node]['dominant']=False
        for test in g.nodes:
            if not is_covered(g, test):
                g.nodes[node]['dominant']=True
                break 
    return g

def begin_cycle_domi(g: nx.Graph) -> nx.Graph:
    partial_domi = nx.Graph()
    cycles = sorted(nx.cycle_basis(g), key= lambda x: len(x), reverse=True)
    if len(cycles)>10:
        largest_cycles = sorted(nx.cycle_basis(g), key= lambda x: len(x), reverse=True)[:10]
    else: 
        largest_cycles = cycles
    for cycle in largest_cycles:
        if mean([g.degree(node) for node in cycle])<=2.2:
            for i, node in enumerate(cycle):
                if i%3==0:
                    neighbours = get_neighbours(g, node)
                    partial_domi.add_edges_from([ ( node, nd) for nd in neighbours])
                    partial_domi.nodes[node]['dominant']=True
                    for nd in neighbours:
                        neighbours_2 = get_neighbours(partial_domi, nd)
                        partial_domi.nodes[nd]['dominant']=False
                        for neighbour in neighbours_2:
                            if not is_covered(partial_domi, neighbour):
                                partial_domi.remove_node(neighbour)
    return partial_domi

                
def dominant(g: nx.Graph):
    """
        A Faire:         
        - Ecrire une fonction qui retourne le dominant du graphe non dirig?? g pass?? en parametre.
        - cette fonction doit retourner la liste des noeuds d'un petit dominant de g

        :param g: le graphe est donn?? dans le format networkx : https://networkx.github.io/documentation/stable/reference/classes/graph.html

    """
    graph = convert_graph_to_int(g)
    partly_domi = begin_cycle_domi(graph)
    domi_graph = greedy_graph(graph, partly_domi)
    purified_graph = purify_graph(domi_graph)
    return [node for node in purified_graph.nodes if purified_graph.nodes[node]['dominant']]



#########################################
#### Ne pas modifier le code suivant ####
#########################################
if __name__=="__main__":
    input_dir = os.path.abspath(sys.argv[1])
    output_dir = os.path.abspath(sys.argv[2])
    
    # un repertoire des graphes en entree doit ??tre pass?? en parametre 1
    if not os.path.isdir(input_dir):
	    print(input_dir, "doesn't exist")
	    exit()

    # un repertoire pour enregistrer les dominants doit ??tre pass?? en parametre 2
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
