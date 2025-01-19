#!/bin/bash

# Function to display usage information
usage() {
    echo "Usage: $0 -g <gender>"
    echo "  -g <gender>  Specify the gender (male/female)"
    exit 1
}

# Check if gender is provided
if [ "$#" -ne 2 ] || [ "$1" != "-g" ]; then
    usage
fi

team_gender=$2

# Define arrays of synonyms and their canonical forms for male and female teams
team_names_male_synonyms=(
    "Laval Rouge-et-Or"
    "Alberta Golden Bears/Pandas"
    "St. Francis Xavier X-Men/X-Women"
    "Laurentian Voyaguers"
    "Sherbrooke Vert-et-Or"
    "UBC Okanagan"
    "UQTR Patriotes"
    "UQAM Citadins"
    "Laurier Golden Hawks"
    # Add more synonyms here
)

team_names_male_canonicals=(
    "Laval Rouge et Or"
    "Alberta Golden Bears"
    "St. F X"
    "Laurentian Voyageurs"
    "Sherbrooke Vert & Or"
    "UBCO Heat"
    "Université du Québec à Trois-Rivières Les Patriote"
    "Université du Québec à Montréal Les Citadins"
    "Wilfrid Laurier Golden Hawks"
    # Add more canonical forms here
)

team_names_female_synonyms=(
    "Laval Rouge-et-Or"
    "Alberta Golden Bears/Pandas"
    "St. Francis Xavier X-Men/X-Women"
    "Laurentian Voyaguers"
    "Sherbrooke Vert-et-Or"
    "UBC Okanagan"
    "UQTR Patriotes"
    "UQAM Citadins"
    "Laurier Golden Hawks"
    # Add more synonyms here
)

team_names_female_canonicals=(
    "Laval Rouge et Or"
    "Alberta Pandas"
    "St. F X"
    "Laurentian Voyageurs"
    "Sherbrooke Vert & Or"
    "UBCO Heat"
    "Université du Québec à Trois-Rivières Les Patriote"
    "Université du Québec à Montréal Les Citadins"
    "Wilfrid Laurier Golden Hawks"
    # Add more canonical forms here
)

# Select the appropriate arrays based on user input
if [[ "$team_gender" == "male" ]]; then
    team_names_synonyms=("${team_names_male_synonyms[@]}")
    team_names_canonicals=("${team_names_male_canonicals[@]}")
elif [[ "$team_gender" == "female" ]]; then
    team_names_synonyms=("${team_names_female_synonyms[@]}")
    team_names_canonicals=("${team_names_female_canonicals[@]}")
else
    echo "Invalid input. Please enter 'male' or 'female'."
    exit 1
fi

# Read from stdin and write to stdout
while IFS= read -r line; do
    for i in "${!team_names_synonyms[@]}"; do
        synonym="${team_names_synonyms[$i]}"
        canonical="${team_names_canonicals[$i]}"
        line="${line//$synonym/$canonical}"
    done
    echo "$line"
done
