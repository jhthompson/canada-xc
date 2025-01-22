import argparse
import csv
import sys

import requests
from bs4 import BeautifulSoup


def fetch_race_results(url, section="women"):
    """
    Fetch and parse race results from a URL to extract name, time, and team information
    for either women's or men's section.
    
    Args:
        url (str): URL of the webpage containing the race results table
        section (str): Either "women" or "men" to specify which section to parse
        
    Returns:
        list: List of dictionaries containing name, time, and team for each runner
    """
    try:
        # Fetch the webpage content
        response = requests.get(url)
        response.raise_for_status()
        
        # Get the HTML content
        html_content = response.text
        
        # Create BeautifulSoup object
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find the race table
        table = soup.find('table', class_='racetable')
        if not table:
            raise ValueError("Could not find race results table on the webpage")
        
        # Initialize results list
        results = []
        
        # Get all rows
        rows = table.find_all('tr')
        
        # Track which section we're in
        in_target_section = False
        parsing_data = False
        
        for row in rows:
            # Check for section headers
            header_cell = row.find('td', class_='h01')
            if header_cell and header_cell.find('h3'):
                header_text = header_cell.h3.text.lower()
                if 'women' in header_text or 'femmes' in header_text:
                    in_target_section = (section == "women")
                    parsing_data = False
                elif 'men' in header_text or 'hommes' in header_text:
                    in_target_section = (section == "men")
                    parsing_data = False
                continue

            # Skip if we're not in our target section
            if not in_target_section:
                continue

            # Handle column headers
            if not parsing_data and row.find('td', class_='h11'):
                parsing_data = True
                continue

            # Parse data rows only when we're in the right section and past headers
            if parsing_data:
                cells = row.find_all('td')
                if len(cells) >= 6:
                    runner = {
                        'name': cells[1].text.strip(),
                        'time': cells[5].text.strip(),
                        'team': cells[2].text.strip(),
                    }
                    results.append(runner)
        
        return results

    except requests.exceptions.RequestException as e:
        raise Exception(f"Error fetching the webpage: {str(e)}")
    except Exception as e:
        raise Exception(f"Error parsing the results: {str(e)}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Parse race results from a webpage and output as CSV')
    parser.add_argument('url', help='URL of the race results page')
    parser.add_argument('--section', choices=['women', 'men'], default='women',
                      help='Which section to parse (default: women)')
    
    # Parse arguments
    args = parser.parse_args()
    
    try:
        # Fetch and parse results
        results = fetch_race_results(args.url, section=args.section)
        
        # Set up CSV writer for stdout
        writer = csv.DictWriter(sys.stdout, fieldnames=['name', 'time', 'team'])
        writer.writeheader()
        writer.writerows(results)
            
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()