import csv
import os
from collections import defaultdict
from datetime import datetime

input_file = "data.csv"  # Replace with your actual CSV file
output_dir = "output_by_created_date"

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Dictionary to collect rows grouped by date (YYYY-MM-DD)
rows_by_date = defaultdict(list)

# Read the input CSV
with open(input_file, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    header = reader.fieldnames

    for row in reader:
        # Extract just the date part of CREATED_DATE
        try:
            full_datetime = datetime.strptime(row['CREATED_DATE'], "%Y-%m-%d %H:%M:%S")
            date_only = full_datetime.date().isoformat()  # 'YYYY-MM-DD'
        except ValueError:
            print(f"Skipping invalid date: {row['CREATED_DATE']}")
            continue

        rows_by_date[date_only].append(row)

# Write each group to a new file
for date_str, rows in rows_by_date.items():
    output_filename = os.path.join(output_dir, f"data_{date_str}.csv")
    
    with open(output_filename, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} rows to {output_filename}")
