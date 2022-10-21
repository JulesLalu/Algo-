from random import random
import sys, os, time
from typing import Optional, Set, List
import networkx as nx

class Node:
    def __init__(self, id: int, choices: int = 0, color: str = 0):
        self.id = id
        self.color = color
        self.choices = choices
        self.dominated = 0


class Graph:
    def __init__(self, g: nx.Graph):
        self.g = g
        id_list =sorted([int(id) for id in g.nodes])
        self.nodes: List[Node] = list(Node(id=id, color='white', choices=len(g.adj[str(id)].keys())+1) for id in id_list)
        self.n_dominated = 0
        self.go_back = False
        self.dominant: List[int] = []
        self.max_degree = max([len([g.adj[str(id)].keys()]) for id in id_list]) + 1
        self.min_size = len(id_list)
        self.min_dom = id_list

    def get_neighbours(self, id: int) -> List[int] :
        return list(int(id) for id in self.g.adj[str(id)].keys())
                

def dominant_rec(id: int, graph: Graph):
    if graph.go_back or (len(graph.dominant)+int((len(graph.nodes)-graph.n_dominated)/graph.max_degree)>=graph.min_size): 
        graph.go_back = False
        return None
    if id==len(graph.nodes):
        if len(graph.dominant) <= graph.min_size:
            graph.min_size = len(graph.dominant)
            graph.min_dom = graph.dominant.copy()
        return None

    neighbours = graph.get_neighbours(id)
    graph.nodes[id].color = 'blue'
    graph.nodes[id].choices -= 1
    for neighbour in neighbours:
        graph.nodes[neighbour].choices -= 1
        if graph.nodes[neighbour].choices == 0 :
            graph.go_back = True

    dominant_rec(id+1, graph)

    for neighbour in neighbours:
        graph.nodes[neighbour].choices += 1

    graph.nodes[id].color = 'red'
    graph.dominant.append(id)
    graph.n_dominated+=len(neighbours)+1
    
    if graph.min_size==len(graph.nodes):
        dominant_rec(id+1, graph)
    else:
        if int(random()*3)==1:
            return dominant_rec(id+1, graph)

    graph.nodes[id].color = 'white'
    graph.dominant.pop()
    graph.n_dominated-=(len(neighbours)+1)
    

def dominant(g: nx.Graph):
    graph = Graph(g)
    dominant_rec(0, graph)
    return graph.min_dom

# def dominant(g: nx.Graph):
#     graph = Graph(g)
#     print([node.id for node in graph.nodes])
#     for node in graph.nodes:
#         print(node.id)
#         if len([node for node in graph.nodes if node.color == 'white'])== 0:
#             print("Breaking")
#             break 
#         neighbours =  graph.get_neighbours(node)
#         for neighbour in neighbours:
#             blue = True
#             if neighbour.choices == 1 and neighbour.dominated == 0:
#                 blue = False
#                 break
#         if blue: 
#             for neighbour in neighbours:
#                 graph.nodes[neighbour.id].choices -=1
#             graph.nodes[node.id].color = 'blue'
#         else:
#             for neighbour in neighbours:
#                 graph.nodes[neighbour.id].dominated +=1
#             graph.nodes[node.id].color = 'red'
#     return [node.id for node in graph.nodes if node.color == 'red']

    

# def dominant(g: nx.Graph):
#     """
#         A Faire:         
#         - Ecrire une fonction qui retourne le dominant du graphe non dirigé g passé en parametre.
#         - cette fonction doit retourner la liste des noeuds d'un petit dominant de g

#         :param g: le graphe est donné dans le format networkx : https://networkx.github.io/documentation/stable/reference/classes/graph.html

#     """
#     graph_nodes = set(g.nodes)
#     current_graph = set()
#     domi = set()
#     while len(current_graph) < len(graph_nodes):
#         nodes_to_add: Set = {}
#         domi_node = 1
#         for node in graph_nodes.difference(domi):
#             new_max = get_neighbours(g, node).difference(current_graph)
#             new_max.add(node)
#             if len(new_max) >= len(nodes_to_add):
#                 nodes_to_add = new_max
#                 domi_node=node
#         domi = domi.union({domi_node})
#         current_graph = current_graph.union(nodes_to_add)
#     return list(domi)



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
