import copy
import threading
from random import randint,choice

import matplotlib.pyplot as mat
import networkx as net
import timeit

from time import sleep
class Task :
    def __init__ (self) :
        self.name=''
        self.reads = []
        self.writes = []
        self.run = None

class TaskSystem :
    
    listTask = []                   #systeme de tache d'entré
    preced = {}                    #dependences parallelisees 
    precedparmax = {}


    def __init__(self, listTask, preced) :         
        
        self.controle(listTask,preced)            #controle d'entré pour listTak et preced

        self.listTask = copy.deepcopy(listTask)            #copie listTask independante de la liste mise en paramettre
        self.preced = copy.deepcopy(preced)           
        #Initialisation dictionnaire de precedence parralelisé
        self.precedparmax = {key.name : [] for key in listTask}
        self.getParMaxSystem()
    

    def controle(self,liste,disk):           #implementation de la fonction controle
        
        if len(liste)!=len(set(liste)):      #vérification de doublons.
            raise ValueError("votre liste de taches contiens des tache dupliquées")    
        task_name=[x.name for x in liste]
        
        #verification de l'existance des taches dans la liste des tache
        for key in disk.keys():
            if (key not in task_name or not(all(x in task_name for x in disk[key])) ):
                raise ValueError("vous avez saisie des taches enixistante")

        #vérifier si toute nos taches sont des clées dans notre disctionnaire de preced 
        if(len(liste)!=len(set(disk.keys()))):
            raise ValueError("votre systeme de presedence manque de taches")
        
        #verifier si le systeme est determiné ou pas
        for i,elt in enumerate(liste):
            for j in liste[i+1:]:
                #verifier si le couple (i,j) verifie les condition de bernstein
                if ((set(elt.reads) & set(j.writes) or set(j.reads) & set(elt.writes) or set(elt.writes) & set(j.writes)) and (self.chemin_rec(elt.name,j.name,disk) and self.chemin_rec(j.name,elt.name,disk))):
                    raise ValueError("systeme non determiné")
    


    def chemin_rec(self,target,source,preced) :      #implementer une fonction recursive chemain rec qui nous retourn vrai si il y'a un chemain de source a target faux sinon
        if (target in preced[source]) :
            return True
        elif (preced[source] == []) :
            return False
        else:
            return any([self.chemin_rec(target,x,preced) for x in preced[source]])
    
    def getParMaxSystem (self) :

        valid_pair=[]     #listes les taches relié par un chmain  
        #reunir toute les pairs relié par un chemain 
        for i, x in enumerate(self.listTask) :

            for y in self.listTask[i+1:]:

                if(self.chemin_rec(x.name,y.name,self.preced)): #verifier si il y'a un chemain de x a y
                    valid_pair.append((x,y))
                elif (self.chemin_rec(y.name,x.name,self.preced)):
                    valid_pair.append((y,x))
        
        #verifier si la condition de bernstein ne s'applique pas sur les couple de valid_paire si oui on ajoute a notre nuveau systeme si non on ajoute pas
        for (x,y) in valid_pair:

            if (set(x.reads) & set(y.writes) or set(y.reads) & set(x.writes) or set(x.writes) & set(y.writes)):
                self.precedparmax[y.name].append(x.name)

        
        work_preced = copy.deepcopy(self.precedparmax)    #creer une copie indepondante de notre dictionnaire parralelisé pour travailler avec
        #On suprime les aretes redondante
        for key in work_preced.keys():

            if len(work_preced[key]) > 1 :
                
                for idx in range (len(work_preced[key])) :
                    save = work_preced[key][idx]              
                    del work_preced[key][idx]                 #suprime pour la clé key la precedence index
                    
                    if (self.chemin_rec(save,key,work_preced)):      # verifier si il y'a un chemain de la valeur suprimer a la clé
                        del self.precedparmax[key][idx]              #si oui il le supprime de notre dictionnaire
                    
                    work_preced[key].insert(idx,save)                
    
    #implementer la fonction de l'execution sequentielle
    def runSeq(self) :
        taskName = {}      #le dictionnaire avec les nom des tache comme clé et les tache elle meme comme valeur
        todo = []         #une liste contenant les taches condidatea s'executer en fonction de leurs precedence
        #remplire taskName avec les tache ordonné par leur ordre d'execution
        while set(self.preced.keys()) != set(taskName.keys()) :

            for key in self.preced.keys():
                #ajouter a todo toute les taches qui peuvent s'executer en fonction de celle qui existe dans taskName
                if (all(task in taskName.keys() for task in self.preced[key]) and key not in taskName.keys()) :
                    todo.append(next((task for task in self.listTask if task.name == key), None))
            while len(todo) != 0:

                insert = choice(todo)            #prendre un element rondome de todo
                taskName[insert.name] = insert    
                todo.remove(insert)            # supprimer l'element
        #executer les tache de taskname en fonction de l'ordre de leurs insertion       
        for id in taskName.keys():
            taskName[id].run()

    #implementé la fonction de l'affichage graphique
    def draw(self):
        graphe=net.DiGraph()         
        graphe.add_nodes_from(x.name for x in self.listTask)     #ajouter toute les taches comme etant des noeuds a mon graphe

        for key in self.precedparmax.keys():

            if len(self.precedparmax[key])!=0:

                for y in self.precedparmax[key]:
                    graphe.add_edge(y,key)                  #ajouter uen arret entre chaque precedent et sa clée
        mat.figure()
        net.draw(graphe, with_labels=True, node_color='skyblue', node_size=2000, font_size=10, font_color='black', font_weight='bold', arrows=True)
        mat.title("Graphe de parallélisme maximale")
        
        mat.show()                  #afficher le graphe
    #implementé la fonction qui nous permetra de controler l'execution des threads
    def handle_function (self,waitevent,setevent,function):
       
        
        if (waitevent == None):         #si la fonction n'attend aucun précedent en cours d'execution
            function()
            setevent.set()                
        else:

            for event in waitevent:         #si la fonction a des precedent en cours d'execution elle attend qu'ils terminent
                event.wait()
            function()
            setevent.set()
    #implementer la fonction du run en parallelle
    def run(self,variables) :
        flags = {task.name : threading.Event() for task in self.listTask}             #un dictionnaire qui associe pour chaque tache un evenement
        taskname = {task.name : task for task in self.listTask}                #un dictionnaire avec les nom des tache comme clé et les taches elle meme comme valeur
        
        for task in self.precedparmax.keys():
            
            if (self.precedparmax[task] == []):       #si l'element n'a aucune precedence
                #lancer un thread sans evenement de precedence
                threading.Thread(target = self.handle_function, args=[None,flags[task],taskname[task].run,variables]).start()               #waitevent = None 
            else:
                waitevent = [flags[dependency] for dependency in self.precedparmax.get(task, [])]         #recuperer les evenements des taches dont elle depend
                threading.Thread(target = self.handle_function, args=[waitevent,flags[task],taskname[task].run,variables]).start()     #passer comme parametre waitevent
        
                    
    def parcost(self):
        temps_par = timeit.timeit(self.run, number=1000)    #calculer le temp que prend run pour faire 1000 executions
        moy_par=temps_par/1000
        temps_sec = timeit.timeit(self.runSeq, number=1000)     #laculer le que prend run_seq pour faire 1000 executions
        moy_sec=temps_sec/1000
        
        if(moy_sec>=moy_par):
            print("pas de chance! l'exection parallele etais plus rapide")
        else:
            print("pas de chance! l'execution sequentielle etais plus rapide")
    


                 