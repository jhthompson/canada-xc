#!/bin/bash

# Check if a URL is provided as a parameter
if [ -z "$1" ]; then
  echo "Usage: $0 <input_url>"
  echo "Please provide the Race Roster URL."
  exit 1
fi

# Define the URL to fetch the JSON data
json_url="$1"

json_data=$(curl "$json_url")

# Print the headers
echo "name,team,time"

# Use jq to parse the JSON and extract the required elements
echo "$json_data" | jq -r '
  .data[] | 
  {
    name: .name,
    team: .teamName,
    time: .gunTime,
  } | 
  "\(.name),\(.team),\(.time)"
'
