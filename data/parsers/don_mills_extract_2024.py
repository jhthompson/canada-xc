import csv

from bs4 import BeautifulSoup


def parse_time(time_str):
    # Return empty string if time is empty
    if not time_str:
        return ""
    return time_str


def clean_team_name(team):
    # Convert team names to proper case and clean up formatting
    return team.strip().title()


def extract_results(html_file, csv_file):
    # Read HTML file
    with open(html_file, encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    # Open CSV file for writing
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "time", "team"])

        # Find all result rows
        rows = soup.select("table.result-table tbody tr")

        for row in rows:
            # Only process rows that have a finishing time
            time_cell = row.select_one("td.time")
            if not time_cell or not time_cell.text.strip():
                continue

            name = row.select_one("td.athlete").text.strip()
            time = parse_time(time_cell.text.strip())
            team = clean_team_name(row.select_one("td.ath-team").text.strip())

            writer.writerow([name, time, team])


if __name__ == "__main__":
    extract_results("don_mills_open_women_2024.html", "don_mills_open_women_2024.csv")
