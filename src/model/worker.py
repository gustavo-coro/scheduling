from typing import List, Optional
from src.model.task import Tier, Task

class Worker:
    def __init__(self, name: str, tier: Tier, regions: List[str], capacity: int):
        self.name = name
        self.tier = tier
        self.regions = regions
        self.capacity = capacity
        self.task_queue = []
        self.current_task = None
        self.available_capacity = capacity
        self.current_load = 0.0

    def can_accept(self, task: Task) -> bool:
        if task.region not in self.regions:
            return False
        if task.tier.value > self.tier.value:
            return False
        if self.available_capacity < task.resource_requirements:
            return False
        return True
    
    def add_task(self, task: Task):
        if not self.can_accept(task):
            raise ValueError("Worker cannot accept this task")
        
        self.task_queue.append(task)
        self.available_capacity -= task.resource_requirements
        self.current_load += task.estimated_duration
        self.task_queue.sort(key=lambda x: (-x.priority.value, x.due_date))

    def process_next_task(self) -> Optional[Task]:
        if not self.task_queue:
            return None
        
        task = self.task_queue.pop(0)
        self.current_task = task
        return task
    
    def complete_current_task(self):
        if self.current_task:
            self.current_task.completed = True
            self.available_capacity += self.current_task.resource_requirements
            self.current_task = None
    
    def get_estimated_completion_time(self) -> float:
        return self.current_load
    
    def get_expected_work_time(self) -> float:
        work_load = 0
        for task in self.task_queue:
            work_load += task.estimated_duration 
        return work_load