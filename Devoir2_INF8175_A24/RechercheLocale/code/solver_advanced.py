# Marsel Bakashov - 2147174
# Prince David Madzou - 2117902

from schedule import Schedule
import random
import time
import math

def solve(schedule : Schedule) -> dict:
    """
    Your solution of the problem
    :param schedule: object describing the input
    :return: a list of tuples of the form (c,t) where c is a course and t a time slot. 
    """
    # Add here your agent
    def naive_solution(schedule): 
        '''
        Start with generating the worst case scenario so it will be easier to converge
        to a easier min global since each step will often help us
        '''
        solution = dict()
        time_slot_idx = 1
        for c in schedule.course_list:
            assignation = time_slot_idx
            solution[c] = assignation
            time_slot_idx += 1
        return solution
    
    def evaluate_solution(solution) -> int:
        '''
        Our objective function, trying to minimize the number of creneaux
        '''
        time_slots = schedule.get_n_creneaux(solution)
        return time_slots
    

    def get_random_neighbor(solution) -> dict:
        """
        This function selects a random course from the solution,
        identifies conflicting slots for that course, and then finds a random available slots
        
        """
        neighbor = solution.copy()

        course = random.choice(list(neighbor.keys()))
        conflicts_slots = {solution[conflict] for conflict in schedule.get_node_conflicts(course)}
        available_slots = [slot for slot in range(len(schedule.course_list)) if slot not in conflicts_slots]

        if available_slots:
            neighbor[course] = random.choice(available_slots)
        
        return neighbor

    def acceptance_probability(delta : float, temperature : float) -> float:
        '''
        Compute the acceptance probability
        '''
        return math.exp(-delta / temperature) if delta > 0 else 1

    def simulated_annealing(t0 : float, alpha : float, time_limit : int) -> dict:
        current_solution = naive_solution(schedule) # generating our naive solution
        current_cost = evaluate_solution(current_solution) # evaluate our current cost from our objective function
        best_solution = current_solution.copy()
        best_cost = current_cost
        temperature = t0
        start_time = time.time()
        
        while time.time() - start_time < time_limit:
            neighbor_solution = get_random_neighbor(current_solution) # generating a random neighbours that fit avalaible spot
            neighbor_cost = evaluate_solution(neighbor_solution) # evaluating the neighbor cost
            delta = neighbor_cost - current_cost
            
            if delta <= 0: # if the cost is lower than the current cost updating our current solution
                current_solution = neighbor_solution
                current_cost = neighbor_cost
            elif delta > 0 and random.random() < acceptance_probability(delta, temperature): # accepting a wrongful nodes with a certain probability dependeing our current temperature
                current_solution = neighbor_solution # updating  our current solution
                current_cost = neighbor_cost

            if current_cost < best_cost: # if the current cost is better than our best solution cost then we update it
                best_solution = current_solution.copy()
                best_cost = current_cost
                print(f"New best solution found with cost {best_cost}")
                
            temperature *= alpha # diminuer la temperature a fur et mesure
            
        return best_solution
    
    return simulated_annealing(100, 0.99, 300)
