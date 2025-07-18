from enum import Enum
from datetime import datetime

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class Tier(Enum):
    TIER1 = 0
    TIER2 = 10
    TIER3 = 15
    TIER4 = 30
    TIER5 = 50

class Resource(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class Task:
    def __init__(self, name: str, priority: Priority, due_date: datetime, region: str, 
                 estimated_duration: float, resource_requirements: Resource, tier: Tier, 
                 arrival_time: float = 0,  # Time when task arrives in system
                 completed: bool = False):
        self.name = name
        self.priority = priority
        self.due_date = due_date
        self.region = region
        self.estimated_duration = estimated_duration
        self.resource_requirements = resource_requirements
        self.tier = tier
        self.arrival_time = arrival_time
        self.completed = completed
    
    def set_priority(self, priority: Priority):
        self.priority = priority
    
    def set_due_date(self, due_date: datetime):
        self.due_date = due_date

    def set_arrival_time(self, arrival_time: datetime):
        self.arrival_time = arrival_time
    
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