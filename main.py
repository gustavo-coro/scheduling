from datetime import datetime, timedelta
from src.model.task import Task, Tier, Priority, Resource
from src.model.worker import Worker
from src.scheduler.grasp import GRASPScheduler

import src.input_handler.input_handler as handler

if __name__ == "__main__":
    workers = [
        Worker("Worker1", Tier.TIER1, ["sa-unknown-1", "sa-southeast-1", "sa-southeast-2"], 1),
        Worker("Worker2", Tier.TIER2, ["sa-unknown-1", "sa-southeast-1", "sa-southeast-3", "sa-southeast-4"], 2),
        Worker("Worker3", Tier.TIER3, ["sa-unknown-1", "sa-southeast-1", "sa-southeast-2", "sa-southeast-3", "sa-southeast-4"], 3),
        Worker("Worker4", Tier.TIER1, ["sa-unknown-1", "sa-southeast-1"], 1),
        Worker("Worker5", Tier.TIER2, ["sa-unknown-1", "sa-southeast-2", "sa-southeast-4"], 3),
        Worker("Worker6", Tier.TIER4, ["sa-unknown-1", "sa-southeast-3"], 2),
        Worker("Worker7", Tier.TIER2, ["sa-unknown-1", "sa-southeast-2", "sa-southeast-3"], 2),
        Worker("Worker8", Tier.TIER3, ["sa-unknown-1", "sa-southeast-1", "sa-southeast-2", "sa-southeast-3", "sa-southeast-4"], 3),
        Worker("Worker9", Tier.TIER2, ["sa-unknown-1", "sa-southeast-1", "sa-southeast-4"], 2),
        Worker("Worker10", Tier.TIER1, ["sa-unknown-1", "sa-southeast-1"], 1),
        Worker("Worker11", Tier.TIER1, ["sa-unknown-1", "sa-southeast-1", "sa-southeast-2", "sa-southeast-3"], 2),
        Worker("Worker12", Tier.TIER2, ["sa-unknown-1", "sa-southeast-1", "sa-southeast-3", "sa-southeast-4"], 3),
        Worker("Worker13", Tier.TIER3, ["sa-unknown-1", "sa-southeast-1", "sa-southeast-2", "sa-southeast-3", "sa-southeast-4"], 3),
        Worker("Worker14", Tier.TIER1, ["sa-unknown-1", "sa-southeast-4"], 1),
        Worker("Worker15", Tier.TIER2, ["sa-unknown-1", "sa-southeast-1", "sa-southeast-2"], 2),
        Worker("Worker16", Tier.TIER1, ["sa-unknown-1", "sa-southeast-3"], 1),
        Worker("Worker17", Tier.TIER2, ["sa-unknown-1", "sa-southeast-1", "sa-southeast-2", "sa-southeast-3"], 2),
        Worker("Worker18", Tier.TIER3, ["sa-unknown-1", "sa-southeast-1", "sa-southeast-2", "sa-southeast-3", "sa-southeast-4"], 3),
        Worker("Worker19", Tier.TIER2, ["sa-unknown-1", "sa-southeast-3", "sa-southeast-3"], 2),
        Worker("Worker20", Tier.TIER1, ["sa-unknown-1", "sa-southeast-1"], 1),
    ]

    tasks = handler.create_tasks_from_csv("output_by_created_date/data_2025-04-06.csv")

    scheduler = GRASPScheduler(workers, alpha=0.2, max_iterations=100)
    best_solution = scheduler.schedule(tasks)

    for worker, assigned_tasks in best_solution.items():
        print(f"\nWorker {worker.name} (Tier {worker.tier.name}, Regions {worker.regions}):")
        for task in assigned_tasks:
            print(f"  - {task.name} (Priority {task.priority.name}, Due {task.due_date}, Duration {task.estimated_duration})")

    violations = scheduler.simulate_execution(best_solution)
    if violations:
        print("\nDue date violations:")
        for task, delay in violations.items():
            print(f"  - {task} will be {delay:.1f} units late")
    else:
        print("\nAll tasks will meet their due dates")