#!/bin/bash

# Check if a URL is provided as a parameter
if [ -z "$1" ]; then
  echo "Usage: $0 <input_url>"
  echo "Please provide the Athletic Live JSON URL (e.g. https://athleticlive.blob.core.windows.net/\$web/ind_res_list/_doc/2926359)."
  exit 1
fi

json_url="$1"
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