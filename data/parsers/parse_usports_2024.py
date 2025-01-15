import csv

from bs4 import BeautifulSoup


def clean_name(name):
    # Convert "LASTNAME, Firstname" to "Firstname Lastname"
    parts = name.strip().split(",")
    if len(parts) == 2:
        lastname = parts[0].strip().title()
        firstname = parts[1].strip().title()
        return f"{firstname} {lastname}"
    return name.strip().title()


def parse_race_results(html_file, output_file):
    # Read HTML file
    with open(html_file, "r") as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, "html.parser")

    # Open CSV file for writing
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["time", "name", "team"])

        # Find all rows in tbody
        rows = soup.find("tbody").find_all("tr")

        for row in rows:
            # Extract only needed cells
            time = row.find_all("td")[2].text.strip()
            raw_name = row.find_all("td")[4].find("a").text.strip()
            team = row.find_all("td")[5].text.strip()

            # Clean up name format
            name = clean_name(raw_name)

            writer.writerow([time, name, team])


if __name__ == "__main__":
    parse_race_results("usports_2024_women.html", "usports_2024_women.csv")
