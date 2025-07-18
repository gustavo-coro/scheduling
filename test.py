from datetime import datetime, timedelta
from src.model.task import Task, Tier, Priority, Resource
from src.model.worker import Worker
from src.scheduler.dynamic_grasp import DynamicGRASPScheduler
from src.scheduler.dynamic_greedy import DynamicGREEDYScheduler

import src.input_handler.input_handler as handler

# Create workers with new tier system
workers = [
    # TIER 5 (2 workers - high capacity, multiple regions)
    Worker("T5-Node1", Tier.TIER5, ["sa-unknown-1", "sa-southeast-1", "sa-southeast-2", "sa-southeast-3", "sa-southeast-4"], 4),
    Worker("T5-Node2", Tier.TIER5, ["sa-unknown-1", "sa-southeast-1", "sa-southeast-3", "sa-southeast-4"], 3),
    
    # TIER 4 (3 workers - medium-high capacity)
    Worker("T4-Node1", Tier.TIER4, ["sa-unknown-1", "sa-southeast-1", "sa-southeast-2"], 3),
    Worker("T4-Node2", Tier.TIER4, ["sa-unknown-1", "sa-southeast-3", "sa-southeast-4"], 2),
    Worker("T4-Node3", Tier.TIER4, ["sa-unknown-1", "sa-southeast-1", "sa-southeast-4"], 2),
    
    # TIER 3 (8 workers - core capacity)
    Worker("T3-Node1", Tier.TIER3, ["sa-unknown-1", "sa-southeast-1", "sa-southeast-2"], 3),
    Worker("T3-Node2", Tier.TIER3, ["sa-unknown-1", "sa-southeast-3", "sa-southeast-4"], 3),
    Worker("T3-Node3", Tier.TIER3, ["sa-unknown-1", "sa-southeast-1", "sa-southeast-3"], 2),
    Worker("T3-Node4", Tier.TIER3, ["sa-unknown-1", "sa-southeast-2", "sa-southeast-4"], 2),
    Worker("T3-Node5", Tier.TIER3, ["sa-unknown-1", "sa-southeast-1", "sa-southeast-4"], 2),
    Worker("T3-Node6", Tier.TIER3, ["sa-unknown-1", "sa-southeast-2", "sa-southeast-3"], 2),
    Worker("T3-Node7", Tier.TIER3, ["sa-unknown-1", "sa-southeast-1"], 3),
    Worker("T3-Node8", Tier.TIER3, ["sa-unknown-1", "sa-southeast-3"], 3),
    
    # TIER 2 (4 workers - medium capacity)
    Worker("T2-Node1", Tier.TIER2, ["sa-unknown-1", "sa-southeast-1"], 2),
    Worker("T2-Node2", Tier.TIER2, ["sa-unknown-1", "sa-southeast-2"], 2),
    Worker("T2-Node3", Tier.TIER2, ["sa-unknown-1", "sa-southeast-3"], 1),
    Worker("T2-Node4", Tier.TIER2, ["sa-unknown-1", "sa-southeast-4"], 1),
    
    # TIER 1 (3 workers - limited capacity)
    Worker("T1-Node1", Tier.TIER1, ["sa-unknown-1"], 1),
    Worker("T1-Node2", Tier.TIER1, ["sa-southeast-1"], 1),
    Worker("T1-Node3", Tier.TIER1, ["sa-southeast-2"], 1)
]

# Create scheduler
scheduler = DynamicGRASPScheduler(workers, alpha=0.3)

# Add tasks with different tiers and resources

tasks = handler.create_tasks_from_csv("output_by_created_date/data_2025-04-06.csv")

for task in tasks:
    scheduler.add_task(task)

# Run 4-hour simulation
scheduler.run_simulation(48*60)