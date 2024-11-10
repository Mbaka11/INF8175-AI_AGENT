from schedule import Schedule
import random
import time
import math
from gc import collect
from cachetools import LFUCache

answer_dict= {
    'A':5,
    'B':6,
    'C':25,
    'D':40,
}



class Solution:

    def __init__(self,schedule: Schedule, teta:int,time_limit:int):
        self.schedule = schedule
        self.enc = {}
        self.best_cost:int | float = float('inf') 
        self.best_solution = dict()
        self.teta = teta
        self.time_limit = time_limit
        self.N = len(self.schedule.course_list)
        self.E = len(self.schedule.conflict_list)
        self._compute_list_conflict()
    
    def _init_encoding(self):
        for c in self.schedule.course_list:
            ...
        

    def __call__(self, *args, **kwds):
        return self.solve(*args, **kwds)

    def _generate_inital_solution(self):
        solution = {c:random.randint(1,self.N) for c in self.schedule.course_list}
        return solution

    def _highest_node_conflict(self,solution:dict[str,int]):
        highest_node = None
        conflit = float('inf')
        
 

    def _generate_random_solution(self):
        index = 0
        solution = dict()
        for c in self.schedule.course_list:
            self.enc[c] = index
            solution[c] = random.randint(1,self.N)
        return solution
            #self.current_solution = {c:random.randint(1,self.N) for c in self.schedule.course_list}
        
    def _gen_valid(self, solution):
        ...
        # current_total_conflit = self.get_total_number_of_conflicts(current_total_conflit)
        # for course in self.schedule.course_list:
        #     skip = solution[course]
        #     for i in range(self.N):
        #         if i != skip:
        #             sol = solution.copy()
        #             sol[course] = i
        #             if self.get_total_number_of_conflicts(sol) <= current_total_conflit:
        #                 yield sol

    def _check_redondant_visitor(self):
        ...

    def _select(self,G):

        ...

    def _evaluation(self,solution):
        return self.schedule.get_n_creneaux(solution)

    def get_total_number_of_conflicts(self,solution) -> int:
        return sum(solution[a[0]] == solution[a[1]] for a in self.schedule.conflict_list)

    def _local_search(self,) -> tuple[int,dict]:
        current_solution = self._generate_random_solution()
        current_cost = self._evaluation(current_solution)
        for _ in range(self.teta):
                G = self._gen_valid(current_solution)

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
        
        print(self.conflict)

    def _regroup_courses(self,solutions):
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
            computed_cost,computed_solution= self._local_search()
            if computed_cost < self.best_cost:
                self.best_solution = computed_solution
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
    return Solution(schedule,1000,10)()
