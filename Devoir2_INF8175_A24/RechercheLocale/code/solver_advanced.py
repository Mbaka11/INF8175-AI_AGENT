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
        solution = dict()
        time_slot_idx = 1
        for c in schedule.course_list:
            assignation = time_slot_idx
            solution[c] = assignation
            time_slot_idx += 1
        return solution
    
    
    def get_total_number_of_conflicts(solution) -> int:
        return sum(solution[a[0]] == solution[a[1]] for a in schedule.conflict_list)
    
    def get_neighborhood(solution) -> list:
        neighbors = []
        for course in schedule.course_list:
            for time_slot in range(len(schedule.course_list)):
                if solution[course] != time_slot:
                    neighbor = solution.copy()
                    neighbor[course] = time_slot
                    neighbors.append(neighbor)
        return neighbors
    
    def get_valid_neighbors(neighbors, solution) -> list:
        current_number_of_conflicts = get_total_number_of_conflicts(solution)
        valid_neighbors = [neighbor for neighbor in neighbors if get_total_number_of_conflicts(neighbor) < current_number_of_conflicts]
        return valid_neighbors
    
    def select_best_neighbor(valid_neighbors) -> dict:
        return min(valid_neighbors, key=lambda sol: schedule.get_n_creneaux(sol))
    
    def evaluate_solution(solution) -> int:
        time_slots = schedule.get_n_creneaux(solution)
        return time_slots
        
    def hill_climbing(current_solution) -> dict:
        # current_solution = {course: random.randint(0, len(schedule.course_list) - 1) for course in schedule.course_list}
        
        while get_total_number_of_conflicts(current_solution) > 0:
            neighbors = get_neighborhood(current_solution)
            valid_neighbors = get_valid_neighbors(neighbors, current_solution)
            if not valid_neighbors:
                valid_neighbors = neighbors
            best_neighbor = select_best_neighbor(valid_neighbors)
            if evaluate_solution(best_neighbor) < evaluate_solution(current_solution):
                current_solution = best_neighbor
            else:
                break

        return current_solution

    def local_search_with_restart(time_limit: int) -> dict:
        start_time = time.time()
        best_solution = hill_climbing()
        best_evaluation = evaluate_solution(best_solution)
        
        while time.time() - start_time < time_limit:
            current_solution = hill_climbing()
            current_evaluation = evaluate_solution(current_solution)
            if current_evaluation < best_evaluation:
                print('New best solution found:', current_evaluation)
                best_solution = current_solution
                best_evaluation = current_evaluation
        
        return best_solution

    def get_random_neighbor(solution) -> dict:
        neighbor = solution.copy()
        course = random.choice(list(neighbor.keys()))
        conflicts_slots = {solution[conflict] for conflict in schedule.get_node_conflicts(course)}
        available_slots = [slot for slot in range(len(schedule.course_list)) if slot not in conflicts_slots]
        
        if available_slots:
            neighbor[course] = random.choice(available_slots)
        
        return neighbor

    def acceptance_probability(delta : float, temperature : float) -> float:
        return math.exp(-delta / temperature) if delta > 0 else 1

    def simulated_annealing(t0 : float, alpha : float, time_limit : int) -> dict:
        current_solution = naive_solution(schedule)
        current_cost = evaluate_solution(current_solution)
        best_solution = current_solution.copy()
        best_cost = current_cost
        temperature = t0
        start_time = time.time()
        
        while time.time() - start_time < time_limit:
            neighbor_solution = get_random_neighbor(current_solution)
            neighbor_cost = evaluate_solution(neighbor_solution)
            delta = neighbor_cost - current_cost
            
            if delta <= 0:
                current_solution = neighbor_solution
                current_cost = neighbor_cost
            elif delta > 0 and random.random() < acceptance_probability(delta, temperature):
                current_solution = neighbor_solution
                current_cost = neighbor_cost

            if current_cost < best_cost:
                best_solution = current_solution.copy()
                best_cost = current_cost
                print(f"New best solution found with cost {best_cost}")
                
            temperature *= alpha
            
        return best_solution
    
    # return hill_climbing()
    # return local_search_with_restart(120)
    return simulated_annealing(100, 0.99, 300)
