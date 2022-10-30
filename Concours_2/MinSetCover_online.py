import sys, os, time
# pour lire un dictionnaire d'un fichier
import ast
from typing import Set
# pour faire la statistique
import numpy
# pour utiliser random, si besoin est
import random

def mon_algo_est_deterministe():
    # par défaut l'algo est considéré comme déterministe
    # changez response = False dans le cas contraire
    response = True
    return response 

##############################################################
# La fonction à completer pour la compétition
##############################################################

# La fonction à completer pour la compétition

def min_set_cover_online(univers_size, collection_size, set_collection_restant, el, covered_already):
    """
        A Faire:         
        - Ecrire une fonction qui retourne la nouvelle coupe

        :univers_size: taille de l'univers
        
        :collection_size: taille de la famille couvrante

        :set_collection_restant: la famille des ensables couvrants NON-UTILISES
 
        :el: un élément courant venant de la séquence, à couvrir 

        :covered_already: éléments déjà couverts par une solution en construction 

        :return l'ensemble couvrant el (None si el déjà couvert) et tous les éléménts déjà couverts par une solution en constuction  
    """
    solution=None
    if el not in covered_already:
        max_len = 0
        for set, elements in set_collection_restant.items():
            if el in elements:
                if len(elements)>max_len:
                    max_len=len(elements)
                    solution = set
                    covered_already = covered_already.union(elements)
    return solution, covered_already


##############################################################
#### LISEZ LE README et NE PAS MODIFIER LE CODE SUIVANT ####
##############################################################
if __name__=="__main__":
    input_dir = os.path.abspath(sys.argv[1])
    output_dir = os.path.abspath(sys.argv[2])
    
    # un repertoire des graphes en entree doit être passé en parametre 1
    if not os.path.isdir(input_dir):
        print(input_dir, "doesn't exist")
        exit()

    # un repertoire pour enregistrer les dominants doit être passé en parametre 2
    if not os.path.isdir(output_dir):
        print(output_dir, "doesn't exist")
        exit()       
	
    # fichier des reponses depose dans le output_dir et annote par date/heure
    output_filename = 'answers_{}.txt'.format(time.strftime("%d%b%Y_%H%M%S", time.localtime()))             
    output_file = open(os.path.join(output_dir, output_filename), 'w')

    # le bloc de lancement dégagé à l'exterieur pour ne pas le répeter pour deterministe/random
    def launching_sequence():
        solution_eleve  = []    
        covered_already = set()
        set_collection_restant = set_collection.copy()
        for el in sequence_a_couvrir:
            # votre algoritme est lancé ici pour un élément courant el
            set_couvrant, covered_already = min_set_cover_online(univers_size, collection_size, set_collection_restant, el, covered_already)
            if set_couvrant is not None :
                solution_eleve.append(set_couvrant)
                del set_collection_restant[set_couvrant]

        # Un algorithme doit toujours tout couvrir (ici, pour vérifier chaque run du randomisé)
        if not set(sequence_a_couvrir).issubset(covered_already):
            print("Couverture n'est pas faite !")
            exit()     
        return solution_eleve, covered_already


    # Collecte des résultats
    scores = []
    
    for instance_filename in sorted(os.listdir(input_dir)):
        
        # C'est une partie pour inserer dans ingestion.py !!!!!
        # importer l'instance depuis le fichier (attention code non robuste)
        # le code repris de Safouan - refaire pour m'affanchir des numéros explicites
        instance_file = open(os.path.join(input_dir, instance_filename), "r")
        lines = instance_file.readlines()
        
        univers_size = int(lines[1])
        collection_size = int(lines[4])
        set_collection = ast.literal_eval(lines[7])
        exact_solution = int(lines[10])
        str_lu_sequence_a_couvrir = lines[13]
        sequence_a_couvrir = ast.literal_eval(str_lu_sequence_a_couvrir)


        # lancement conditionelle de votre algorithme
        # N.B. il est lancé par la fonction launching_sequence() 
        if mon_algo_est_deterministe():
            print("lancement d'un algo deterministe")  
            solution_eleve, covered_already = launching_sequence()
            # la composition de la solution perd son intérêt, conversion vers sa longueur
            # aussi pour être cohérent avec la solution randomisé
            solution_eleve=len(solution_eleve)  
        else:
            print("lancement d'un algo randomisé")
            runs = 10
            sample = numpy.empty(runs)
            for r in range(runs):
                solution_eleve, covered_already = launching_sequence()  
                sample[r] = len(solution_eleve)
            solution_eleve = numpy.mean(sample)


        best_ratio = solution_eleve/float(exact_solution)
        scores.append(best_ratio)
        # ajout au rapport
        output_file.write(instance_filename + ': score: {}\n'.format(best_ratio))

    output_file.write("Résultat moyen des ratios:" + str(sum(scores)/len(scores)))

    output_file.close()

