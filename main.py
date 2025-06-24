from datetime import date, timedelta
from src.model.task import Task, Tier, Priority
from src.model.worker import Worker
from src.scheduler.grasp import GRASPScheduler

if __name__ == "__main__":
    workers = [
        Worker("Worker1", Tier.TIER3, ["Europe", "North America"], 5),
        Worker("Worker2", Tier.TIER2, ["Asia", "Europe"], 12),
        Worker("Worker3", Tier.TIER1, ["North America"], 5),
        Worker("Worker4", Tier.TIER3, ["North America", "Asia"], 10),
    ]

    tasks = [
        Task("Task1", Priority.HIGH, date.today() + timedelta(days=15), "Europe", 10.0, 4, Tier.TIER3),
        Task("Task2", Priority.MEDIUM, date.today() + timedelta(days=18), "Asia", 8.0, 2, Tier.TIER2),
        Task("Task3", Priority.LOW, date.today() + timedelta(days=15), "North America", 5.0, 1, Tier.TIER1),
        Task("Task4", Priority.LOW, date.today() + timedelta(days=15), "North America", 4.0, 1, Tier.TIER1),
        Task("Task5", Priority.LOW, date.today() + timedelta(days=24), "Asia", 4.0, 1, Tier.TIER2),
        Task("Task6", Priority.LOW, date.today() + timedelta(days=19), "Asia", 5.0, 1, Tier.TIER1),
        Task("Task7", Priority.HIGH, date.today() + timedelta(days=16), "North America", 10.0, 4, Tier.TIER3),
        Task("Task8", Priority.MEDIUM, date.today() + timedelta(days=18), "Asia", 6.0, 2, Tier.TIER2),
        Task("Task9", Priority.MEDIUM, date.today() + timedelta(days=19), "Asia", 8.0, 2, Tier.TIER3),
        Task("Task10", Priority.LOW, date.today() + timedelta(days=18), "Europe", 5.0, 1, Tier.TIER1),
        Task("Task11", Priority.MEDIUM, date.today() + timedelta(days=15), "Asia", 6.0, 2, Tier.TIER2),
        Task("Task12", Priority.LOW, date.today() + timedelta(days=16), "Europe", 4.0, 1, Tier.TIER1),

    ]

    scheduler = GRASPScheduler(workers, alpha=0.3, max_iterations=50)
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