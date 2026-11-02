# canada-xc
Django application storing cross country information in Canada

## Import AthleticLIVE results

Create the meet and an empty race in the Django admin, then run:

```sh
python manage.py import_athletic_live <race_id> \
  https://data.athletic.live/ind_res_list/_doc/2939642
```

The command imports names, finish times (including fractional seconds), teams,
and supplied scoring points. Zero points mean excluded from scoring and are
stored as blank, not zero. DNF, DNS, DQ, and DSQ entries are skipped because
results require a finish time. The source sex must match the selected race;
verify the race distance and meet date yourself.

Teams must already exist and match by full name, short name, or the existing
team aliases. An unknown or ambiguous team cancels the entire import. Existing
race results are never overwritten. Runner profiles are not created or assigned;
use `python manage.py assign_runners <race_id>` afterwards if needed.
