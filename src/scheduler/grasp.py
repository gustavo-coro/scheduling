from typing import List, Dict
from datetime import datetime
import random
import copy
from src.model.task import Task
from src.model.worker import Worker

class GRASPScheduler:
    def __init__(self, workers: List[Worker], alpha: float = 0.9, max_iterations: int = 100):
        self.workers = workers
        self.alpha = alpha
        self.max_iterations = max_iterations
    
    def schedule(self, tasks: List[Task]) -> Dict[Worker, List[Task]]:
        best_solution = None
        best_score = float('-inf')
        
        for _ in range(self.max_iterations):
            solution = self.construct_solution(copy.deepcopy(tasks))
            improved_solution = self.local_search(solution)
            current_score = self.evaluate_solution(improved_solution)
            
            if current_score > best_score:
                best_score = current_score
                best_solution = improved_solution
        
        return best_solution
    
    def construct_solution(self, tasks: List[Task]) -> Dict[Worker, List[Task]]:
        for worker in self.workers:
            worker.task_queue = []
            worker.current_task = None
            worker.available_capacity = worker.capacity
            worker.current_load = 0.0

        tasks.sort(key=lambda x: (-x.priority.value, x.due_date))
        
        solution = {worker: [] for worker in self.workers}
        
        for task in tasks:
            feasible_workers = [w for w in self.workers if w.can_accept(task)]
            
            if not feasible_workers:
                print(f"Warning: No feasible worker found for task {task.name}")
                continue

            worker_scores = []
            for worker in feasible_workers:
                score = worker.current_load
                worker_scores.append((score, worker))

            worker_scores.sort(key=lambda x: x[0])
            min_score = worker_scores[0][0]
            max_score = worker_scores[-1][0]
            threshold = min_score + self.alpha * (max_score - min_score)
            rcl = [ws[1] for ws in worker_scores if ws[0] <= threshold]
            selected_worker = random.choice(rcl)
            selected_worker.add_task(task)
            solution[selected_worker].append(task)
        
        return solution
    
    def local_search(self, solution: Dict[Worker, List[Task]]) -> Dict[Worker, List[Task]]:
        improved = True
        max_passes = 10
        passes = 0
        
        while improved and passes < max_passes:
            improved = False
            passes += 1

            for worker1, tasks1 in solution.items():
                for worker2, tasks2 in solution.items():
                    if worker1 == worker2:
                        continue
                    for i, task1 in enumerate(tasks1):
                        for j, task2 in enumerate(tasks2):
                            if (worker1.can_accept(task2) and worker2.can_accept(task1) and
                                self._swap_improves(worker1, task1, worker2, task2)):
                                tasks1[i], tasks2[j] = tasks2[j], tasks1[i]
                                worker1.task_queue.remove(task1)
                                worker2.task_queue.remove(task2)
                                worker1.add_task(task2)
                                worker2.add_task(task1)
                                improved = True
                                break
                        if improved:
                            break
                    if improved:
                        break
                if improved:
                    break
        
        return solution
    
    def _swap_improves(self, worker1: Worker, task1: Task, worker2: Worker, task2: Task) -> bool:
        original_load_diff = abs(worker1.current_load - worker2.current_load)
        new_load1 = worker1.current_load - task1.estimated_duration + task2.estimated_duration
        new_load2 = worker2.current_load - task2.estimated_duration + task1.estimated_duration
        new_load_diff = abs(new_load1 - new_load2)
        return new_load_diff < original_load_diff
    
    def evaluate_solution(self, solution: Dict[Worker, List[Task]]) -> float:
        makespan = max(w.current_load for w in self.workers)
        priority_score = sum(-t.priority.value for w in self.workers for t in w.task_queue)
        current_time = 0
        due_date_penalty = 0
        for worker in self.workers:
            completion_time = current_time
            for task in worker.task_queue:
                completion_time += task.estimated_duration
                if completion_time > (task.due_date - datetime.now().date()).days:
                    due_date_penalty += 100

        score = -makespan + priority_score - due_date_penalty
        return score
    
    def simulate_execution(self, solution: Dict[Worker, List[Task]]) -> Dict[str, float]:
        worker_timelines = {worker.name: 0.0 for worker in self.workers}
        violations = {}
        
        while True:
            next_worker = None
            next_time = float('inf')
            
            for worker in self.workers:
                if worker.task_queue:
                    completion_time = worker_timelines[worker.name] + worker.task_queue[0].estimated_duration
                    if completion_time < next_time:
                        next_time = completion_time
                        next_worker = worker
            
            if not next_worker:
                break

            task = next_worker.task_queue.pop(0)
            worker_timelines[next_worker.name] = next_time
            due_in_days = (task.due_date - datetime.now().date()).days
            if next_time > due_in_days:
                violations[task.name] = next_time - due_in_days
        
        return violations