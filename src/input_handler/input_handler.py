import csv
from datetime import datetime
from src.model.task import Task, Priority, Tier, Resource


def parse_date(date_str: str):
    try:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d %H:%M:%S")
    except ValueError:
        print(f"Warning: Invalid date format '{date_str}'. Using None.")
        return None

def create_tasks_from_csv(file_path: str) -> list[Task]:
    tasks = []
    
    try:
        with open(file_path, mode='r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            
            for row_num, row in enumerate(reader, 1):
                if len(row) < 8:
                    print(f"Warning: Row {row_num} has insufficient columns. Skipping.")
                    continue
                
                try:
                    # DUE_TO,CREATED_DATE,REGION,TIER,PRIORITY,ESTIMATED_DURATION,MAXIMUM_WAITING_TIME,RESOURCE_REQUIREMENT
                    due_date = parse_date(row[0])
                    creted_date = parse_date(row[1])
                    region = row[2].strip()
                    tier = int(row[3].strip())
                    priority = row[4].strip().upper()
                    duration = float(row[5].strip())
                    max_wait = float(row[6].strip())
                    resource = row[7].strip().upper()

                    if duration < 0:
                        duration = 5.0


                    task = Task(f"{row_num}", Priority.MEDIUM, due_date, region, duration, Resource.MEDIUM, Tier.TIER2, creted_date)
                    
                    try:
                        task.set_priority(Priority[priority])
                    except KeyError:
                        print(f"Warning: Invalid priority '{priority}' in row {row_num}. Using MEDIUM.")
                        task.set_priority(Priority.MEDIUM)

                    try:
                        task.add_resource_requirement(Resource[resource])
                    except KeyError:
                        print(f"Warning: Invalid resource '{resource}' in row {row_num}. Using MEDIUM.")
                        task.set_priority(Resource.MEDIUM)
                    
                    try:
                        task.set_tier(Tier(tier))
                    except KeyError:
                        print(f"Warning: Invalid tier '{tier}' in row {row_num}. Using TIER2.")
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