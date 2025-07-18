from enum import Enum
import random
from typing import List, Optional
from datetime import datetime
import copy
from src.model.task import Task
from src.model.worker import Worker
from heapq import heappush, heappop

class EventType(Enum):
    TASK_ARRIVAL = 1
    TASK_COMPLETION = 2

class Event:
    def __init__(self, event_type: EventType, time: float, task: Optional[Task] = None):
        self.event_type = event_type
        self.time = time  # Simulation time in minutes
        self.task = task
    
    def __lt__(self, other):
        return self.time < other.time

class DynamicGRASPScheduler:
    def __init__(self, workers: List[Worker], alpha: float = 0.3):
        self.workers = workers
        self.alpha = alpha  # GRASP randomness parameter
        self.event_queue = []
        self.current_time = 0  # Minutes
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
        """Run simulation with proper task processing"""
        print(f"\nStarting GRASP simulation (α={self.alpha})")
        
        while self.event_queue and self.current_time <= end_time_minutes:
            event = heappop(self.event_queue)
            self.current_time = event.time
            
            if event.event_type == EventType.TASK_ARRIVAL:
                self._handle_task_arrival(event.task)
            elif event.event_type == EventType.TASK_COMPLETION:
                self._handle_task_completion(event.task)
            
            # Only run scheduler when workers are idle
            if any(w.current_task is None for w in self.workers):
                self._run_grasp_scheduler()
        
        # Final cleanup
        self._complete_remaining_tasks()
        print(f"\nSimulation completed at {self._format_time(self.current_time)}")
        self._print_final_stats()

    def _complete_remaining_tasks(self):
        """Ensure all assigned tasks are processed"""
        while any(w.task_queue or w.current_task for w in self.workers):
            # Find next task completion
            next_time = float('inf')
            next_worker = None
            
            for worker in self.workers:
                if worker.current_task:
                    completion_time = self.current_time + worker.current_task.estimated_duration
                    if completion_time < next_time:
                        next_time = completion_time
                        next_worker = worker
            
            if next_worker:
                self.current_time = next_time
                next_worker.complete_current_task()
                print(f"[{self._format_time(self.current_time)}] {next_worker.name} "
                      f"completed task")
                self._assign_next_task(next_worker)

    def _handle_task_arrival(self, task: Task):
        """Process new task arrival"""
        self.pending_tasks.append(task)
        print(f"[{self._format_time(self.current_time)}] Task '{task.name}' arrived")

    def _handle_task_completion(self, task: Task):
        """Process task completion and start next task"""
        for worker in self.workers:
            if worker.current_task == task:
                worker.complete_current_task()
                worker.current_load -= task.estimated_duration
                print(f"[{self._format_time(self.current_time)}] {worker.name} "
                      f"completed '{task.name}'")
                self._assign_next_task(worker)
                break

    def _run_grasp_scheduler(self):
        """GRASP scheduling for idle workers"""
        if not self.pending_tasks:
            return
        
        print(f"[{self._format_time(self.current_time)}] Running scheduler...")
        
        best_solution = None
        best_score = float('-inf')
        
        # Limited iterations for dynamic environment
        for _ in range(3):
            solution = self._construct_grasp_solution()
            solution = self._local_search(solution)
            current_score = self._evaluate_solution(solution)
            
            if current_score > best_score:
                best_score = current_score
                best_solution = solution
        
        if best_solution:
            self._apply_solution(best_solution)

    def _construct_grasp_solution(self):
        """Greedy randomized construction"""
        temp_workers = copy.deepcopy([w for w in self.workers if w.current_task is None])
        solution = {w: [] for w in temp_workers}
        
        for task in sorted(self.pending_tasks,
                         key=lambda x: (-x.priority.value, x.due_date.timestamp() 
                                      if isinstance(x.due_date, datetime) 
                                      else x.due_date)):
            feasible_workers = [w for w in temp_workers if w.can_accept(task)]
            
            if not feasible_workers:
                continue
            
            worker_scores = []
            for worker in feasible_workers:
                slack = self._calculate_slack(worker, task)
                score = worker.current_load - (0.5 * slack)
                worker_scores.append((score, worker))
            
            # Create RCL
            worker_scores.sort(key=lambda x: x[0])
            min_score = worker_scores[0][0]
            max_score = worker_scores[-1][0]
            threshold = min_score + self.alpha * (max_score - min_score)
            rcl = [ws[1] for ws in worker_scores if ws[0] <= threshold]
            
            if rcl:
                selected_worker = random.choice(rcl)
                selected_worker.add_task(task)
                solution[selected_worker].append(task)
        
        return solution
    
    def _calculate_slack(self, worker: Worker, task: Task) -> float:
        """Calculate time slack before deadline"""
        if isinstance(task.due_date, datetime):
            deadline_min = (task.due_date.timestamp() / 60) + self.time_offset
        else:
            deadline_min = task.due_date
        
        return deadline_min - (self.current_time + worker.current_load)

    def _local_search(self, solution):
        """Simple swap-based local search"""
        improved = True
        max_iterations = 10
        
        while improved and max_iterations > 0:
            improved = False
            max_iterations -= 1
            
            for worker1, tasks1 in solution.items():
                for worker2, tasks2 in solution.items():
                    if worker1 == worker2:
                        continue
                    
                    # Try all possible swaps between workers
                    for i, task1 in enumerate(tasks1):
                        for j, task2 in enumerate(tasks2):
                            if (worker1.can_accept(task2) and 
                                worker2.can_accept(task1) and
                                self._swap_improves(worker1, task1, worker2, task2)):
                                
                                # Perform swap
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

    def _evaluate_solution(self, solution) -> float:
        """Evaluate solution quality"""
        # 1. Load balance
        loads = [w.current_load for w in solution.keys()]
        load_imbalance = max(loads) - min(loads) if loads else 0
        
        # 2. Priority satisfaction
        priority_score = 0
        for worker, tasks in solution.items():
            for task in tasks:
                weight = {3: 10, 2: 5, 1: 1}[task.priority.value]
                priority_score += weight
        
        # 3. Deadline adherence
        deadline_score = 0
        for worker, tasks in solution.items():
            completion_time = self.current_time + worker.current_load
            for task in tasks:
                if isinstance(task.due_date, datetime):
                    deadline_min = (task.due_date.timestamp() / 60) + self.time_offset
                else:
                    deadline_min = task.due_date
                
                if completion_time <= deadline_min:
                    deadline_score += 1
                completion_time += task.estimated_duration
        
        # Combined score (higher is better)
        return -load_imbalance + priority_score + deadline_score

    def _apply_solution(self, solution):
        """Apply the best found solution"""
        for worker, tasks in solution.items():
            real_worker = next(w for w in self.workers if w.name == worker.name)
            
            # Clear current queue (except running task)
            if real_worker.current_task is None:
                real_worker.task_queue = []
                real_worker.current_load = 0
            
            # Add new assignments
            for task in tasks:
                if task not in real_worker.task_queue:
                    real_worker.add_task(task)
            
            # Start processing if idle
            if real_worker.current_task is None and real_worker.task_queue:
                self._assign_next_task(real_worker)
        
        # Update pending tasks
        self.pending_tasks = [t for t in self.pending_tasks 
                             if not any(t in w.task_queue for w in self.workers)]

    def _assign_next_task(self, worker: Worker):
        """Start next task on worker if available"""
        if worker.task_queue and worker.current_task is None:
            next_task = worker.process_next_task()
            completion_time = self.current_time + next_task.estimated_duration
            heappush(self.event_queue,
                   Event(EventType.TASK_COMPLETION, completion_time, next_task))
            print(f"[{self._format_time(self.current_time)}] {worker.name} "
                  f"started '{next_task.name}' "
                  f"(ETA: {self._format_time(completion_time)})")

    def _swap_improves(self, worker1, task1, worker2, task2) -> bool:
        """Check if swapping tasks improves solution"""
        # Calculate current and new loads
        current_diff = abs(worker1.current_load - worker2.current_load)
        
        new_load1 = worker1.current_load - task1.estimated_duration + task2.estimated_duration
        new_load2 = worker2.current_load - task2.estimated_duration + task1.estimated_duration
        new_diff = abs(new_load1 - new_load2)
        
        return new_diff < current_diff

    def _format_time(self, minutes: float) -> str:
        """Convert minutes to HH:MM format"""
        return f"{int(minutes//60):02d}:{int(minutes%60):02d}"

    def _print_final_stats(self):
        """Print simulation summary"""
        print("\n=== Simulation Results ===")
        print(f"Total runtime: {self._format_time(self.current_time)}")
        
        print("\nWorker Utilization:")
        for worker in self.workers:
            utilization = (worker.current_load / self.current_time) * 100 if self.current_time > 0 else 0
            print(f"{worker.name} (Tier {worker.tier.name}):")
            print(f"  - Utilization: {utilization:.1f}%")
            print(f"  - Queued tasks: {len(worker.task_queue)}")
            if worker.current_task:
                print(f"  - Current task: {worker.current_task.name}")
        
        print("\nPending Tasks:", len(self.pending_tasks))
        for task in self.pending_tasks:
            print(f"- '{task.name}' (Tier: {task.tier.name}, Resources: {task.resource_requirements.name})")