import csv
import json


def format_team_name(team):
    # Convert team abbreviation to proper case
    if not team:
        return ""
    return team.title()

def parse_results(json_file):
    # Read JSON file
    with open(json_file) as f:
        data = json.load(f)
    
    # List to store formatted results
    results = []
    
    # Extract results from the 'r' array
    for runner in data.get('_source').get('r', []):
        result = {
            'name': f"{runner.get('a').get('n')}".strip(),
            'time': runner.get('m', ''),
            'team': format_team_name(runner.get('a').get('t').get('n'))
        }
        results.append(result)
    
    return results

def write_csv(results, output_file):
    # Write results to CSV
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'time', 'team'])
        writer.writeheader()
        writer.writerows(results)

def main():
    input_file = 'marauder_invitational_men_2024.json'
    output_file = 'marauder_invitational_men_2024.csv'
    
    try:
        results = parse_results(input_file)
        write_csv(results, output_file)
        print(f"Successfully wrote {len(results)} results to {output_file}")
    except Exception as e:
        print(f"Error processing results: {e}")

if __name__ == '__main__':
    main()