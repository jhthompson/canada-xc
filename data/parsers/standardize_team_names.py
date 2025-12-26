import argparse
import sys

common_team_names = {
    # synonym: canonical
    "Laval Rouge-et-Or": "Laval Rouge et Or",
    "Laval Rouge et Or": "Laval Rouge et Or",
    "Universite Laval": "Laval Rouge et Or",
    "Universit� de Sherbrooke": "Sherbrooke Vert & Or",
    "Sherbrooke Vert-et-Or": "Sherbrooke Vert & Or",
    "UBC Okanagan": "UBCO Heat",
    "Ubc Okanagan": "UBCO Heat",
    "UQTR Patriotes": "Université du Québec à Trois-Rivières Les Patriote",
    "UQTR": "Université du Québec à Trois-Rivières Les Patriote",
    "UQAM Citadins": "Université du Québec à Montréal Les Citadins",
    "UQAM": "Université du Québec à Montréal Les Citadins",
    "UQAC": "UQAC Inuk",
    "Universite Quebec A Montreal": "Université du Québec à Montréal Les Citadins",
    "Laurier Golden Hawks": "Wilfrid Laurier Golden Hawks",
    "Wilfrid Laurier University": "Wilfrid Laurier Golden Hawks",
    "McGill University": "McGill Redbirds",
    "University of Guelph": "Guelph Gryphons",
    "Trinity Western University": "Trinity Western Spartans",
    "Western": "Western Mustangs",
    "Western University": "Western Mustangs",
    "University of Calgary": "Calgary Dinos",
    "Queens Gaels": "Queen's Gaels",
    "Queen's University": "Queen's Gaels",
    "Queens University": "Queen's Gaels",
    "McMaster University": "McMaster Marauders",
    "University of Windsor": "Windsor Lancers",
    "University of Victoria": "Victoria Vikes",
    "University of Regina": "Regina Cougars",
    "Dalhousie University": "Dalhousie Tigers",
    "University of Toronto": "Toronto Varsity Blues",
    "University of Prince Edward Island": "UPEI Panthers",
    "University of PEI": "UPEI Panthers",
    "University of P E I": "UPEI Panthers",
    "Brock University": "Brock Badgers",
    "Saint Marys University": "St. Mary's Huskies",
    "St Mary's": "St. Mary's Huskies",
    "Saint Marys": "St. Mary's Huskies",
    "Saint Mary's": "St. Mary's Huskies",
    "Saint Mary's University": "St. Mary's Huskies",
    "St. Mary's Huskies Univeristy": "St. Mary's Huskies",
    "Montreal Carabins": "Montréal Carabins",
    "Universite de Montreal": "Montréal Carabins",
    "Universite De Montreal": "Montréal Carabins",
    "University of Manitoba": "Manitoba Bisons",
    "University of Ottawa": "Ottawa Gee-Gees",
    "University of Waterloo": "Waterloo Warriors",
    "MacEwan University": "MacEwan Griffins",
    "Thompson Rivers University": "Thompson Rivers Wolfpack",
    "Universite de Moncton": "Moncton Aigles Bleu",
    "University de Moncton": "Moncton Aigles Bleu",
    "University of Saskatchewan": "Saskatchewan Huskies",
    # "Carleton University": "Carleton Ravens",
    "Carleton": "Carleton Ravens",
    "Lakehead University": "Lakehead Thunderwolves",
    "Laurentian University": "Laurentian Voyageurs",
    "St Francis Xavier University": "St. F X",
    "St. Francis Xavier University": "St. F X",
    "St. Francis Xavier": "St. F X",
    "St. Francis": "St. F X",
    "StFX": "St. F X",
    "St F X": "St. F X",
    "Acadia University": "Acadia",
    "Ryerson University": "Ryerson Rams",
    "Concordia University": "Concordia Stingers",
    "University of New Brunswick": "UNB Reds",
    "U N B": "UNB Reds",
    "Memorial University of Newfoundland": "Memorial Sea-Hawks",
    "St. Thomas University": "St. Thomas Tommies",
    "St. Thomas": "St. Thomas Tommies",
    "St Thomas": "St. Thomas Tommies",
    "A S E A": "ASEA Athlétisme Sud-Est / South-East Athletics",
    "unattached": "Unattached",
    "Y H Z Athletics": "YHZ Athletics",
    "St Francis Xavier X-Men/X-Women": "St. F X",
    "Toronto Metro Bold": "TMU Bold",
    "Ecole de technologie superieure": "École de technologie supérieure",
}

male_team_names = {
    # synonym: canonical
    "Alberta Golden Bears/Pandas": "Alberta Golden Bears",
    "University of Alberta": "Alberta Golden Bears",
    "McGill Martlets/Redmen": "McGill Redbirds",
    "McGill University": "McGill Redbirds",
    "McGill": "McGill Redbirds",
}

female_team_names = {
    # synonym: canonical
    "Alberta Golden Bears/Pandas": "Alberta Pandas",
    "University of Alberta": "Alberta Pandas",
    "McGill Martlets/Redmen": "McGill Martlets",
    "McGill University": "McGill Martlets",
    "McGill": "McGill Martlets",
}


def main():
    parser = argparse.ArgumentParser(description="Standardize team names.")
    parser.add_argument(
        "-g",
        "--gender",
        required=True,
        choices=["male", "female"],
        help="Specify the gender (male/female)",
    )
    args = parser.parse_args()

    team_gender = args.gender

    if team_gender == "male":
        team_names = common_team_names | male_team_names
    elif team_gender == "female":
        team_names = common_team_names | female_team_names
    else:
        print("Invalid input. Please enter 'male' or 'female'.")
        sys.exit(1)

    # Read from stdin and write to stdout
    for line in sys.stdin:
        for synonym, canonical in team_names.items():
            line = line.replace(synonym, canonical)
        print(line, end="")


if __name__ == "__main__":
    main()
