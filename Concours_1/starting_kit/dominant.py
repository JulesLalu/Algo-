from random import random
import sys, os, time
from typing import Optional, Set, List
import networkx as nx

def get_neighbours(g: nx.Graph, node: int) -> Set[int]:
    return {int(node) for node in g.adj[str(node)].keys()}
                
def dominant(g: nx.Graph):
    """
        A Faire:         
        - Ecrire une fonction qui retourne le dominant du graphe non dirigé g passé en parametre.
        - cette fonction doit retourner la liste des noeuds d'un petit dominant de g

        :param g: le graphe est donné dans le format networkx : https://networkx.github.io/documentation/stable/reference/classes/graph.html

    """
    graph_nodes = set(g.nodes)
    current_graph = set()
    domi = set()
    while len(current_graph) < len(graph_nodes):
        nodes_to_add: Set = {}
        domi_node = 1
        for node in graph_nodes.difference(domi):
            new_max = get_neighbours(g, node).difference(current_graph)
            new_max.add(node)
            if len(new_max) >= len(nodes_to_add):
                nodes_to_add = new_max
                domi_node=node
        domi = domi.union({domi_node})
        current_graph = current_graph.union(nodes_to_add)
    return list(domi)



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
        output_file.write('\n')
        
    output_file.close()
