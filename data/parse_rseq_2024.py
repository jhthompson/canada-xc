from bs4 import BeautifulSoup
import csv

def parse_race_results(html_file, output_file):
    # Read HTML file
    with open(html_file, 'r') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Open CSV file for writing
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['name', 'team', 'time'])
        
        # Find all result rows
        rows = soup.find('tbody').find_all('tr')
        
        for row in rows:
            # Extract data using data-bind attributes
            name = row.find('td', {'data-bind': lambda x: x and 'text: FullName' in x}).text.strip()
            team = row.find('td', {'data-bind': lambda x: x and 'text: TeamName' in x}).text.strip()
            time = row.find('td', {'data-bind': lambda x: x and 'text: GunElapsedFormatted' in x}).text.strip()
            
            writer.writerow([name, team, time])

if __name__ == '__main__':
    parse_race_results('rseq_championships_women_2024.html', 'rseq_championships_women_2024.csv')