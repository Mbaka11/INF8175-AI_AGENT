from schedule import Schedule
import random
import time
import math
from gc import collect
from cachetools import LFUCache

answer_dict= {
    'instances/horaire_A_11_20.txt':4,
    'instances/horaire_B_23_71.txt':5,
    'instances/horaire_C_121_3960.txt':11,
    'instances/horaire_D_645_13979.txt':31,
}



class Solution:

    def __init__(self,schedule: Schedule, t0:int,teta:int,time_limit:int):
        self.schedule = schedule
        self.enc = {}

        self.t0 = t0
        self.miss = 0
        self.hit = 0

        self.best_cost:int | float = float('inf') 
        self.best_solution = dict()

        self.teta = teta
        self.time_limit = time_limit

        self.N = len(self.schedule.course_list)
        self.E = len(self.schedule.conflict_list)
        self.cache = LFUCache(100)
        self.list_cache:list[list[frozenset]] = []
        self._compute_list_conflict()
    
    def __call__(self, *args, **kwds):
        return self.solve(*args, **kwds)

    def _highest_node_conflict(self,group,solution):

        #group= self._regroup_courses(solution)

        temp_result= {}

        for course, creance in solution.items():
            brotherz = group[creance].difference([course])
            size = len(brotherz.intersection(self.conflict[course]))
            
            if size not in temp_result:
                temp_result[size] = set()

            temp_result[size].add(course)
        
        max_key = max(temp_result.keys())
        return random.choice(list(temp_result[max_key]))

    def naive_solution(self):
        solution = dict()
        time_slot_idx = 1
        for c in self.schedule.course_list:
            assignation = time_slot_idx
            solution[c] = assignation
            time_slot_idx += 1
        return solution


    def _generate_random_solution(self):
        index = 0
        solution = dict()
        for c in self.schedule.course_list:
            self.enc[c] = index
            solution[c] = random.randint(1,self.N)
        return solution
            #self.current_solution = {c:random.randint(1,self.N) for c in self.schedule.course_list}
        
    def _gen_valid(self,highest_node,solution):
        current_total_conflict = self.get_total_number_of_conflicts(solution)
        skip = solution[highest_node]
        for i in range(self.N):
            if i != skip:
                sol = solution.copy()
                sol[highest_node] = i
                total_conflict = self.get_total_number_of_conflicts(sol) 
                if total_conflict < current_total_conflict or total_conflict == 0:
                    yield sol
        # current_total_conflit = self.get_total_number_of_conflicts(solution)
        # for course in self.schedule.course_list:
        #     skip = solution[course]
        #     for i in range(self.N):
        #         if i != skip:
        #             sol = solution.copy()
        #             sol[course] = i
        #             if self.get_total_number_of_conflicts(sol) <= current_total_conflit:
        #                 yield sol

    def _compute_redondant_visitor(self,group:dict):
        grouped_frozensets = set()
        for val in group.values(): grouped_frozensets.add(frozenset(val))

        if grouped_frozensets not in self.list_cache:
            self.list_cache.append(grouped_frozensets)
            return False
        return True
        

    def _select(self,G,current_solution,current_cost):

        counter = 0
        best_cost = math.inf
        best_sol= None

        for sol in G:
            counter+=1
            cost = self._evaluation(sol)
            if cost < best_cost:
                best_sol = sol.copy()
                best_cost = cost

        if counter==0:
            return  current_solution,current_cost

        return best_sol,cost
        
    def _evaluation(self,solution):
        return self.schedule.get_n_creneaux(solution)

    def get_total_number_of_conflicts(self,solution) -> int:
        return sum(solution[a[0]] == solution[a[1]] for a in self.schedule.conflict_list)

    def _local_search(self) -> tuple[int,dict]:
        current_solution = self._generate_random_solution()
        current_cost = self._evaluation(current_solution)
        
        best_solution =current_solution.copy()
        best_cost = current_cost

        for _ in range(self.teta):
            group = self._regroup_courses(current_solution)
            if self._compute_redondant_visitor(group):
                self.hit += 1
                #print(self.hit)
                continue
            highest_conflict_course = self._highest_node_conflict(group,current_solution)
            G = self._gen_valid(highest_conflict_course,current_solution)
            current_solution,cost = self._select(G,current_solution,current_cost)
            if  cost < best_cost:
                best_cost = cost
                best_solution =current_solution.copy()
                print('\tNew Local Search cost: ',best_cost)
        return best_cost,best_solution 

    def _compute_list_conflict(self):
        self.conflict:dict[str,set] = {}
        for  conflict in self.schedule.conflict_list:
            
            a,b = conflict
            if a not in self.conflict:
                self.conflict[a] = set()  
            if b not in self.conflict:
                self.conflict[b] = set()

            self.conflict[a].add(b)
            self.conflict[b].add(a)

    def _regroup_courses(self,solutions) -> dict[int,set] :
        dico_groupes = {}
        for courses, vals in solutions.items():
            if vals not in dico_groupes:
                dico_groupes[vals] = set()
            dico_groupes[vals].add(courses)
    
        return dico_groupes
    
    def solve(self,):
        print('Solving...')
        start_time = time.time()
        while time.time() - start_time < self.time_limit:
            #print('New restart at ',time.time()-start_time, ' seconds')
            computed_cost,computed_solution= self._local_search()
            if computed_cost < self.best_cost:
                print('Computed best solution: ',computed_cost)
                try:
                    flag= self.schedule.verify_solution(computed_solution)
                except: 
                    flag = False
                
                if flag:
                    print('New best solution cost: ',computed_cost)
                    self.best_solution = computed_solution.copy()
                    self.best_cost = computed_cost



        return self.best_solution

def solve(schedule : Schedule) -> dict:
    """
    Your solution of the problem
    :param schedule: object describing the input
    :return: a list of tuples of the form (c,t) where c is a course and t a time slot. 
    """
    
    # Add here your agent
    
    # return hill_climbing()
    # return local_search_with_restart(120)
    return Solution(schedule,300,300)()
