#!/bin/bash

# A function to make words plural by adding an s
# when the value ($2) is != 1 or -1
# It only adds an 's'; it is not very smart.
# https://www.oreilly.com/library/view/bash-cookbook/0596526784/ch13s08.html
#
function plural ()
{
    if [ "$2" -eq 1 ] || [ "$2" -eq -1 ]
    then
        echo "${1}"
    else
        echo "${1}"s
    fi
}

# current date
date=$(date '+%Y-%m-%d') # YYYY-MM-DD

# clone production database
SECONDS=0
echo "⏰ Cloning production database..."
ssh jeremy@canadaxc.ca /bin/bash << EOF > prod-"${date}".dump
 pg_dump canadaxc --format=custom --no-acl --no-owner
EOF
echo ✅ Took $SECONDS "$(plural second $SECONDS)"
echo

# load into local database
SECONDS=0
echo "⏰ Recreating local database..."
dropdb canadaxc
createdb canadaxc --owner=django
pg_restore --no-privileges --no-owner --role=django --clean --if-exists --dbname=canadaxc prod-"${date}".dump 
echo ✅ Took $SECONDS "$(plural second $SECONDS)"
echo