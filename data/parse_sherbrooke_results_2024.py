import csv
import json
from datetime import timedelta
from math import ceil


def format_time(microseconds):
    # Create timedelta and format it
    time_delta = timedelta(microseconds=microseconds)
    
    # Extract hours, minutes, seconds
    hours = int(time_delta.total_seconds() // 3600)
    minutes = int((time_delta.total_seconds() % 3600) // 60)
    seconds = ceil(time_delta.total_seconds() % 60)
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

# Read JSON file
with open('sherbrooke_invitational_women_2024.json') as file:
    data = json.load(file)

# Prepare data for CSV
csv_data = []
for result in data['results']:
    participant = result['participant']
    name = f"{participant['firstName']} {participant['lastName']}"
    team = participant['team']
    time = format_time(result['totalDuration'])
    csv_data.append({
        'name': name,
        'team': team,
        'time': time
    })

# Write to CSV
with open('sherbrooke_invitational_female_2024.csv', 'w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=['name', 'team', 'time'])
    writer.writeheader()
    writer.writerows(csv_data)