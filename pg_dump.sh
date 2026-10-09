#!/bin/bash

# current date
date=$(date '+%Y-%m-%d') # YYYY-MM-DD

# clone production database
echo "⏰ Cloning production database..."
ssh jeremy@canadaxc.ca /bin/bash << EOF > prod-"${date}".dump
 pg_dump canadaxc --format=custom --no-acl --no-owner
EOF
echo