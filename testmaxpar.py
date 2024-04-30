from maxpar import *
from random import uniform
from time import sleep
from multiprocessing import Queue,Process

global_vars=[2]*5    #liste de variable globales initié a 5 cases de 2
# declarer les fonction de tests
def runT1():
    global global_vars
    sleep(uniform(0,2))
    global_vars[3] = global_vars[0] + 2
    #print('im task 1')
    return global_vars[3]

def runT2():
    global global_vars
    sleep(uniform(0,2))
    global_vars[0] = 2 * global_vars[0] + global_vars[3] + global_vars[2]
    #print('im task 2')
    return global_vars[0]

def runT3():
    global global_vars
    sleep(uniform(0,2))
    global_vars[4] = global_vars[3] + global_vars[2]
    #print('im task 3')
    return global_vars[4]

def runT4():
    global global_vars
    sleep(uniform(0,2))
    global_vars[1] = 2 * global_vars[3]
    #print('im task 4')
    return global_vars[1]

def runT5():
    global global_vars
    sleep(uniform(0,2))
    global_vars[4] = 2 * global_vars[4] 
    #print('im task 5')
    return global_vars[4]

def runT6():
    global global_vars
    sleep(uniform(0,2))
    global_vars[3] = 2 * global_vars[0] + 2 * global_vars[1]
    #print('im task 6')
    return global_vars[3]
 #crer des taches pour tester avec l'Instantance de la classe task
t1 = Task()
t1.name = "T1"
t1.writes = ["M4"]
t1.reads=["M1"]
t1.run = runT1

t2 = Task()
t2.name = "T2"
t2.reads = ["M3","M4"]
t2.writes =["M1"]
t2.run = runT2

t3 = Task()
t3.name = "T3"
t3.reads = ["M3", "M4"]
t3.writes = ["M5"]
t3.run = runT3

t4 = Task()
t4.name = "T4"
t4.reads = ["M4"]
t4.writes = ["M2"]
t4.run = runT4

t5 = Task()
t5.name = "T5"
t5.reads = ["M5"]
t5.writes = ["M5"]
t5.run = runT5

t6 = Task()
t6.name = "T6"
t6.reads = ["M1", "M2"]
t6.writes = ["M4"]
t6.run = runT6
tasks = [t1,t2,t3,t4,t5,t6]
#implementé une fonction qui chnage les valeurs des variables globale
def change_globals (change) :
    global global_vars

    for i in range(0,len(global_vars)) :
        global_vars[i] = change[i]
# implementer une fonction qui execute les processus
def handle_rand_function(function,local_vars,queue):
    change_globals(local_vars)
    function()
    queue.put(global_vars)
# implementer la fonction qui fait des teste de determinisation randomisé
"""ps: On a utilisé les processus car contrairement au threads chaque processus prend une copie de la memoire et travail avec
cela est plus adapté quand plusieurs executions sont lancé de maniere parallele car dans le cas contraire on aura jamais un 
resultat correcte du moment ou chaque execution modefie les varibale globales en parallele"""
def detTestRnd(sysTask) :
    for k in range(1,8):       #le nombre de jeux de valeur aleatoire a effectuer
        local_results = {}        #un dictionnaire avec les resultat de chaque thread
        queues = []         # une liste de file d'attente des processus
        processes = []            #la liste des processus a executer
        local_vars = [randint(0,10) for _ in range(6)]
        #executer
        for i in range(0,2):
            queue = Queue()         
            queues.append(queue)
            processes.append(Process(target=handle_rand_function,args = [sysTask.runSeq,local_vars,queue]))
            processes[i].start()
        
        for i in range (len(processes)) :
            processes[i].join()
            local_results[i] = queues[i].get()
        first_elt = next(iter(local_results.values()),[])

        all_same = all(elt == first_elt for elt in local_results.values())

        if not all_same:
            print("Le systeme n'est pas determine")
            return 1

    print("Le systeme est determine")


def main() :

    s1 = TaskSystem(tasks, {"T1" : [], "T2" : ["T1"],"T3" : ["T1"],"T4" : ["T1","T2"],"T5" : ["T3"],"T6":["T5","T4"] })
    s1.draw()









if __name__ == '__main__' :
    main()