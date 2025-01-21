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
    ",Laval Rouge-et-Or"
    ",Universite Laval"
    ",Alberta Golden Bears/Pandas"
    ",University of Alberta"
    ",St. Francis Xavier X-Men/X-Women"
    ",St. Francis Xavier"
    ",Laurentian Voyaguers"
    ",Sherbrooke Vert-et-Or"
    ",Sherbrooke"
    ",UBC Okanagan"
    ",UQTR Patriotes"
    ",UQTR"
    ",UQAM Citadins"
    ",UQAM"
    ",Laurier Golden Hawks"
    ",Wilfrid Laurier University"
    ",McGill Martlets/Redmen"
    ",McGill University"
    ",University of Guelph"
    ",Western University"
    ",University of Calgary"
    ",Queen's University"
    ",McMaster University"
    ",University of Windsor"
    ",Trinity Western University"
    ",University of Victoria"
    ",University of Regina"
    ",Dalhousie University"
    ",University of Toronto"
    ",University of PEI"
    ",Brock University"
    ",Saint Mary's University"
    ",Universite de Montreal"
    ",University of Manitoba"
    ",University of Ottawa"
    ",University of Waterloo"
    ",MacEwan University"
    ",Thompson Rivers University"
    ",Universite de Moncton"
    # Add more synonyms here
)

team_names_male_canonicals=(
    ",Laval Rouge et Or"
    ",Laval Rouge et Or"
    ",Alberta Golden Bears"
    ",Alberta Golden Bears"
    ",St. F X"
    ",St. F X"
    ",Laurentian Voyageurs"
    ",Sherbrooke Vert & Or"
    ",Sherbrooke Vert & Or"
    ",UBCO Heat"
    ",Université du Québec à Trois-Rivières Les Patriote"
    ",Université du Québec à Trois-Rivières Les Patriote"
    ",Université du Québec à Montréal Les Citadins"
    ",Université du Québec à Montréal Les Citadins"
    ",Wilfrid Laurier Golden Hawks"
    ",Wilfrid Laurier Golden Hawks"
    ",McGill Redbirds"
    ",McGill Redbirds"
    ",Guelph Gryphons"
    ",Western Mustangs"
    ",Calgary Dinos"
    ",Queen's Gaels"
    ",McMaster Marauders"
    ",Windsor Lancers"
    ",Trinity Western Spartans"
    ",Victoria Vikes"
    ",Regina Cougars"
    ",Dalhousie Tigers"
    ",Toronto Varsity Blues"
    ",UPEI Panthers"
    ",Brock Badgers"
    ",St. Mary's Huskies"
    ",Montréal Carabins"
    ",Manitoba Bisons"
    ",Ottawa Gee-Gees"
    ",Waterloo Warriors"
    ",MacEwan Griffins"
    ",Thompson Rivers Wolfpack"
    ",Moncton Aigles Bleu"
    # Add more canonical forms here
)

team_names_female_synonyms=(
    ",Laval Rouge-et-Or"
    ",Universite Laval"
    ",Alberta Golden Bears/Pandas"
    ",University of Alberta"
    ",St. Francis Xavier X-Men/X-Women"
    ",St. Francis Xavier"
    ",Laurentian Voyaguers"
    ",Laurentian University"
    ",Sherbrooke Vert-et-Or"
    ",Sherbrooke"
    ",UBC Okanagan"
    ",UQTR Patriotes"
    ",UQAM Citadins"
    ",UQAM"
    ",Laurier Golden Hawks"
    ",Wilfrid Laurier University"
    ",McGill Martlets/Redmen"
    ",Acadia Axemen/Axewomen"
    ",Acadia University"
    ",McGill University"
    ",University of Guelph"
    ",Western University"
    ",University of Calgary"
    ",Queen's University"
    ",McMaster University"
    ",University of Windsor"
    ",Trinity Western University"
    ",University of Victoria"
    ",University of Regina"
    ",Dalhousie University"
    ",University of Toronto"
    ",University of PEI"
    ",Brock University"
    ",Saint Mary's University"
    ",Universite de Montreal"
    ",University of Manitoba"
    ",University of Ottawa"
    ",University of Waterloo"
    ",MacEwan University"
    ",Thompson Rivers University"
    ",Universite de Moncton"
    ",University of Saskatchewan"
    ",Carleton University"
    ",Lakehead University"
    # Add more synonyms here
)

team_names_female_canonicals=(
    ",Laval Rouge et Or"
    ",Laval Rouge et Or"
    ",Alberta Pandas"
    ",Alberta Pandas"
    ",St. F X"
    ",St. F X"
    ",Laurentian Voyageurs"
    ",Laurentian Voyageurs"
    ",Sherbrooke Vert & Or"
    ",Sherbrooke Vert & Or"
    ",UBCO Heat"
    ",Université du Québec à Trois-Rivières Les Patriote"
    ",Université du Québec à Montréal Les Citadins"
    ",Université du Québec à Montréal Les Citadins"
    ",Wilfrid Laurier Golden Hawks"
    ",Wilfrid Laurier Golden Hawks"
    ",McGill Martlets"
    ",Acadia"
    ",Acadia"
    ",McGill Redbirds"
    ",Guelph Gryphons"
    ",Western Mustangs"
    ",Calgary Dinos"
    ",Queen's Gaels"
    ",McMaster Marauders"
    ",Windsor Lancers"
    ",Trinity Western Spartans"
    ",Victoria Vikes"
    ",Regina Cougars"
    ",Dalhousie Tigers"
    ",Toronto Varsity Blues"
    ",UPEI Panthers"
    ",Brock Badgers"
    ",St. Mary's Huskies"
    ",Montréal Carabins"
    ",Manitoba Bisons"
    ",Ottawa Gee-Gees"
    ",Waterloo Warriors"
    ",MacEwan Griffins"
    ",Thompson Rivers Wolfpack"
    ",Moncton Aigles Bleu"
    ",Saskatchewan Huskies"
    ",Carleton Ravens"
    ",Lakehead Thunderwolves"
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
