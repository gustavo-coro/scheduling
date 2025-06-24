from typing import List, Dict
from datetime import datetime
import copy
from src.model.task import Task
from src.model.worker import Worker

class GREEDYScheduler:
    def __init__(self, workers: List[Worker]):
        self.workers = workers
    
    def schedule(self, tasks: List[Task]) -> Dict[Worker, List[Task]]:
        solution = self.construct_solution(copy.deepcopy(tasks))
        
        return solution
    
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
            selected_worker = worker_scores[0][1]
            selected_worker.add_task(task)
            solution[selected_worker].append(task)
        
        return solution
    
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