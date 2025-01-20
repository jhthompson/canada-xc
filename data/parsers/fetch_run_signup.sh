#!/bin/bash

# Check if URL is provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 <url>"
    exit 1
fi

URL=$1

json_data=$(curl -H 'Accept: application/json, */*; q=0.01' -s "$URL")

# Create the CSV header
echo "name,time,team"

# Fetch JSON from URL and parse using jq
echo "$json_data" | jq -r '.resultSet.results[] | [
  .[2],           # name (index 2)
  .[24],          # chip time (index 24)
  .[3]            # team (index 3)
] | join(",")'

# Check if curl or jq failed
if [ $? -ne 0 ]; then
    echo "Error: Failed to fetch or parse data"
    exit 1
fi