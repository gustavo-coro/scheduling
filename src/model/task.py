from enum import Enum
from datetime import date

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class Tier(Enum):
    TIER1 = 1
    TIER2 = 2
    TIER3 = 3

class Task:
    def __init__(self, name: str, priority: Priority, due_date: date, region: str, 
                 estimated_duration: float, resource_requirements: int, tier: Tier, 
                 completed: bool = False):
        self.name = name
        self.priority = priority
        self.due_date = due_date
        self.region = region
        self.estimated_duration = estimated_duration
        self.resource_requirements = resource_requirements
        self.tier = tier
        self.completed = completed
    
    def set_priority(self, priority: Priority):
        self.priority = priority
    
    def set_due_date(self, due_date: date):
        self.due_date = due_date
    
    def set_region(self, region: str):
        self.region = region
    
    def set_estimated_duration(self, time: float):
        if time >= 0:
            self.estimated_duration = time
    
    def add_resource_requirement(self, resource: int):
        self.resource_requirements = resource
    
    def set_tier(self, tier: Tier):
        self.tier = tier
    
    def mark_completed(self):
        self.completed = True

    def __lt__(self, other):
        return self.priority.value > other.priority.value