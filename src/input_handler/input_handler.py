import csv
from datetime import datetime
from src.model.task import Task, Priority, Tier


def parse_due_date(date_str: str):
    try:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
    except ValueError:
        print(f"Warning: Invalid date format '{date_str}'. Using None.")
        return None

def create_tasks_from_csv(file_path: str) -> list[Task]:
    tasks = []
    
    try:
        with open(file_path, mode='r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            
            for row_num, row in enumerate(reader, 1):
                if len(row) < 6:
                    print(f"Warning: Row {row_num} has insufficient columns. Skipping.")
                    continue
                
                try:
                    priority_str = row[0].strip().upper()
                    due_date = parse_due_date(row[1])
                    region = row[2].strip()
                    duration = float(row[3].strip())
                    resources = [r.strip() for r in row[4].split(';') if r.strip()]
                    tier_str = row[5].strip().upper()
                    task = Task(f"Task-{row_num}", f"Imported from CSV row {row_num}")
                    try:
                        task.set_priority(Priority[priority_str])
                    except KeyError:
                        print(f"Warning: Invalid priority '{priority_str}' in row {row_num}. Using MEDIUM.")
                        task.set_priority(Priority.MEDIUM)
                    
                    task.set_due_date(due_date)
                    task.set_region(region)
                    task.set_estimated_duration(duration)
                    
                    for resource in resources:
                        task.add_resource_requirement(resource)
                    
                    try:
                        task.set_tier(Tier[tier_str])
                    except KeyError:
                        print(f"Warning: Invalid tier '{tier_str}' in row {row_num}. Using TIER2.")
                        task.set_tier(Tier.TIER2)
                    
                    tasks.append(task)
                    
                except ValueError as e:
                    print(f"Error processing row {row_num}: {e}. Skipping.")
    
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []
    
    return tasks