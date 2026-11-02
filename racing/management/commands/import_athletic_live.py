import json
import re
from urllib.error import URLError
from urllib.request import Request, urlopen

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from racing.hytek import match_teams, parse_finish_time
from racing.models import Race, Result


class Command(BaseCommand):
    help = "Import AthleticLIVE individual results into an existing, empty race."

    def add_arguments(self, parser):
        parser.add_argument("race_id", type=int)
        parser.add_argument(
            "url", help="https://data.athletic.live/ind_res_list/_doc/<id>"
        )

    def handle(self, *args, **options):
        url = options["url"]
        if not re.fullmatch(
            r"https://data\.athletic\.live/ind_res_list/_doc/[0-9]+", url
        ):
            raise CommandError("URL must be an AthleticLIVE individual results URL.")
        request = Request(
            url, headers={"User-Agent": "canada-xc/0.1", "Accept": "application/json"}
        )
        try:
            with urlopen(request, timeout=30) as response:
                source = json.loads(response.read())["_source"]
        except (URLError, OSError, ValueError, KeyError, TypeError) as error:
            raise CommandError(
                f"Could not fetch AthleticLIVE results: {error}"
            ) from error

        with transaction.atomic():
            try:
                race = Race.objects.select_for_update().get(pk=options["race_id"])
            except Race.DoesNotExist as error:
                raise CommandError("Race does not exist.") from error
            if race.result_set.exists():
                raise CommandError("This race already has results; import cancelled.")
            try:
                sex = {"Male": "M", "Female": "F", "Mixed": "X"}[source["g"]]
                if sex != race.sex:
                    raise ValueError("Source sex does not match the selected race.")
                entries = source["r"]
                if not isinstance(entries, list):
                    raise ValueError("Expected a list of individual results.")
                rows, skipped = [], 0
                for entry in entries:
                    mark = entry["m"]
                    if mark in {"DNF", "DNS", "DQ", "DSQ"}:
                        skipped += 1
                        continue
                    if not re.fullmatch(r"(?:\d+:)?\d+:[0-5]\d(?:\.\d+)?", mark):
                        raise ValueError(f"Invalid finish time: {mark}")
                    points = entry.get("pt")
                    if points is not None and (type(points) is not int or points < 0):
                        raise ValueError(f"Invalid points: {points}")
                    rows.append(
                        {
                            "name": entry["a"]["n"].strip(),
                            "raw_team": entry["a"]["t"]["n"],
                            "time": parse_finish_time(mark),
                            # AthleticLIVE uses zero for athletes excluded from scoring.
                            "points": points or None,
                        }
                    )
                if not rows:
                    raise ValueError("No individual finishers found.")
                results = []
                for row in match_teams(rows, race.sex):
                    if len(row["teams"]) != 1:
                        raise ValueError(
                            "Team must match exactly one existing team: "
                            f"{row['raw_team']}"
                        )
                    result = Result(
                        race=race,
                        name=row["name"],
                        time=row["time"],
                        points=row["points"],
                        team_id=row["teams"][0]["id"],
                    )
                    result.full_clean()
                    results.append(result)
            except (
                KeyError,
                TypeError,
                AttributeError,
                ValueError,
                ValidationError,
            ) as error:
                raise CommandError(f"Invalid AthleticLIVE results: {error}") from error
            Result.objects.bulk_create(results)
        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {len(results)} results into race {race.pk}; "
                f"skipped {skipped} non-finishers."
            )
        )
