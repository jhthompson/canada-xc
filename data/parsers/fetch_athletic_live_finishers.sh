#!/bin/bash

# Check if a URL is provided as a parameter
if [ -z "$1" ]; then
  echo "Usage: $0 <input_url>"
  echo "Please provide the Athletic Live URL (e.g. https://live.athletic.net/meets/39707/events/xc/1502595)."
  exit 1
fi

# Extract the final number from the URL
event_id=$(echo "$1" | sed 's:.*/::')
echo "Fetching data for event ID: $event_id"

# Define the URL to fetch the JSON data
json_url="https://athleticlive.blob.core.windows.net/\$web/ind_res_list/_doc/1031951"

json_data=$(curl "$json_url")

# Print the headers
echo "name,time,team,points"

# Use jq to parse the JSON and extract the required elements
echo "$json_data" | jq -r '
  ._source.r[] | 
  {
    name: .a.n,
    time: .m,
    team: .a.t.n,
    points: (if .pt == 0 then "" else .pt end)
  } | 
  "\(.name),\(.time),\(.team),\(.points)"
'