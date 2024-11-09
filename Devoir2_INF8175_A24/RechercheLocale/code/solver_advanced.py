from schedule import Schedule
import random
import time
import math




class Solution:

    def __init__(self,schedule: Schedule):
        self.schedule = schedule
        self.best_solution = None
        self.N = len(self.schedule.conflict_list)
        self.E = len(self.schedule.conflict_list)
        
    def __call__(self, *args, **kwds):
        ...

    def _parse_solution_to_schedule(self):
        ...

    def _generate_solution(self):
        ...

    def _gen_valid(self):
        ...

    def _check_redondant_vistor(self):
        ...

    def _select(self):
        ...

    def _evaluation(self):
        ...
    
    def solve(self):
        ...

    

        pass

def solve(schedule : Schedule) -> dict:
    """
    Your solution of the problem
    :param schedule: object describing the input
    :return: a list of tuples of the form (c,t) where c is a course and t a time slot. 
    """

    print(schedule.course_list)
    # Add here your agent
    
    # return hill_climbing()
    # return local_search_with_restart(120)
    ...
