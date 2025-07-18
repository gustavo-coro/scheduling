from typing import List, Optional
from enum import Enum
from heapq import heappush, heappop
from src.model.task import Task
from src.model.worker import Worker
from datetime import datetime

class EventType(Enum):
    TASK_ARRIVAL = 1
    TASK_COMPLETION = 2

class Event:
    def __init__(self, event_type: EventType, time: float, task: Optional[Task] = None):
        self.event_type = event_type
        self.time = time
        self.task = task
    
    def __lt__(self, other):
        return self.time < other.time

class DynamicGREEDYScheduler:
    def __init__(self, workers: List[Worker]):
        self.workers = workers
        self.event_queue = []
        self.current_time = 0  # Simulation time in minutes
        self.pending_tasks = []
        self.time_offset = 0  # For normalizing past timestamps
        self.simulation_started = False
    
    def add_task(self, task: Task):
        """Add task with proper time normalization"""
        if not isinstance(task.arrival_time, (float, int)):
            # Convert datetime arrival_time to minutes since epoch
            arrival_epoch = task.arrival_time.timestamp() / 60
            
            if not self.simulation_started:
                # Set time offset based on earliest task
                self.time_offset = -arrival_epoch
                self.simulation_started = True
            
            task.arrival_time = arrival_epoch + self.time_offset
        
        heappush(self.event_queue, Event(EventType.TASK_ARRIVAL, task.arrival_time, task))
    
    def run_simulation(self, end_time_minutes: float = 8*60):
        """Run simulation for specified duration (default 8 hours)"""
        print(f"\nStarting simulation (current offset: {self._format_time(self.time_offset*60)})")
        
        while self.event_queue and self.current_time <= end_time_minutes:
            event = heappop(self.event_queue)
            self.current_time = event.time
            
            if event.event_type == EventType.TASK_ARRIVAL:
                self._handle_task_arrival(event.task)
            elif event.event_type == EventType.TASK_COMPLETION:
                self._handle_task_completion(event.task)
            
            self._schedule_pending_tasks()
        
        print(f"\nSimulation ended at {self._format_time(self.current_time)}")
        self._print_final_stats()

    def _handle_task_arrival(self, task: Task):
        """Process new task arrival"""
        self.pending_tasks.append(task)
        print(f"[{self._format_time(self.current_time)}] Task '{task.name}' arrived | "
              f"Priority: {task.priority.name} | "
              f"Duration: {task.estimated_duration} mins | "
              f"Tier: {task.tier.name} | "
              f"Resources: {task.resource_requirements.name}")

    def _handle_task_completion(self, task: Task):
        """Process task completion"""
        for worker in self.workers:
            if worker.current_task == task:
                worker.complete_current_task()
                worker.current_load -= task.estimated_duration
                print(f"[{self._format_time(self.current_time)}] {worker.name} "
                      f"completed '{task.name}' (was {task.priority.name} priority)")
                self._assign_next_task(worker)
                break

    def _schedule_pending_tasks(self):
        """Assign tasks using greedy approach with new tier/resource logic"""
        # Sort by priority (HIGH first), then earliest deadline
        self.pending_tasks.sort(key=lambda x: (
            -x.priority.value,
            x.due_date.timestamp() if isinstance(x.due_date, datetime) else x.due_date
        ))
        
        for task in self.pending_tasks[:]:
            feasible_workers = [
                w for w in self.workers 
                if w.can_accept(task) and 
                self._can_complete_on_time(w, task)
            ]
            
            if not feasible_workers:
                continue
                
            # Select worker with minimum current load
            selected_worker = min(feasible_workers, key=lambda w: w.current_load)
            selected_worker.add_task(task)
            self.pending_tasks.remove(task)
            
            print(f"[{self._format_time(self.current_time)}] Assigned '{task.name}' "
                  f"to {selected_worker.name} (Tier {selected_worker.tier.name})")
            
            if selected_worker.current_task is None:
                self._assign_next_task(selected_worker)

    def _assign_next_task(self, worker: Worker):
        """Start processing next task on worker"""
        if worker.task_queue and worker.current_task is None:
            next_task = worker.process_next_task()
            completion_time = self.current_time + next_task.estimated_duration
            heappush(self.event_queue,
                   Event(EventType.TASK_COMPLETION, completion_time, next_task))
            
            print(f"[{self._format_time(self.current_time)}] {worker.name} "
                  f"started '{next_task.name}' "
                  f"(ETA: {self._format_time(completion_time)})")

    def _can_complete_on_time(self, worker: Worker, task: Task) -> bool:
        """Check if task can be completed before deadline"""
        if isinstance(task.due_date, datetime):
            deadline_min = (task.due_date.timestamp() / 60) + self.time_offset
        else:
            deadline_min = task.due_date
            
        estimated_end = self.current_time + worker.current_load + task.estimated_duration
        return estimated_end <= deadline_min

    def _format_time(self, minutes: float) -> str:
        """Convert minutes to HH:MM format"""
        return f"{int(minutes//60):02d}:{int(minutes%60):02d}"

    def _print_final_stats(self):
        """Print simulation summary"""
        print("\n=== Final Statistics ===")
        print(f"Total simulation time: {self._format_time(self.current_time)}")
        
        print("\nWorker Utilization:")
        for worker in self.workers:
            utilization = (worker.current_load / self.current_time) * 100 if self.current_time > 0 else 0
            pending = len(worker.task_queue)
            print(f"{worker.name} (Tier {worker.tier.name}):")
            print(f"  - Utilization: {utilization:.1f}%")
            print(f"  - Pending tasks: {pending}")
            if worker.current_task:
                print(f"  - Current task: {worker.current_task.name}")
        
        print("\nPending Tasks:", len(self.pending_tasks))
        for task in self.pending_tasks:
            deadline = self._format_deadline(task.due_date)
            print(f"- '{task.name}' (Due: {deadline}, Tier: {task.tier.name})")

    def _format_deadline(self, due_date) -> str:
        """Format deadline for display"""
        if isinstance(due_date, datetime):
            deadline_min = (due_date.timestamp() / 60) + self.time_offset
            return f"{self._format_time(deadline_min)} (original: {due_date.strftime('%Y-%m-%d %H:%M')})"
        return f"{self._format_time(due_date)}"