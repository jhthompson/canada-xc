"""Hy-Tek PDF parsing and result-matching helpers."""

import re
from datetime import timedelta

import pdfplumber

from data.parsers.standardize_team_names import (
    common_team_names,
    female_team_names,
    male_team_names,
)
from racing.models import Team

RESULT = re.compile(
    r"^\s*(\d+)\s+(.+?)\s{2,}(.+?)\s+(\d{1,2}:\d{2}(?:\.\d+)?)\s*(\d+)?\s*$"
)
EVENT = re.compile(r"\.{3,}Event\s+\d+\s+(.+)|Event\s+\d+\s+(.+)")


def parse_pdf(file) -> list[dict]:
    rows, event, in_results = [], "", False
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            for line in (page.extract_text(layout=True) or "").splitlines():
                match = EVENT.search(line)
                if match:
                    event = (match.group(1) or match.group(2)).strip()
                    in_results = False
                elif "Team Scores" in line:
                    in_results = False
                elif line.strip().startswith("Results -"):
                    in_results = True
                elif in_results and (match := RESULT.match(line)):
                    place, name, team, time, points = match.groups()
                    rows.append(
                        dict(
                            event=event,
                            place=place,
                            name=name.strip(),
                            raw_team=team.strip(),
                            time=time,
                            points=points or "",
                        )
                    )
    if not rows:
        raise ValueError("No individual results found in this PDF")
    return rows


def parse_finish_time(value: str) -> timedelta:
    parts = [float(part) for part in value.split(":")]
    if len(parts) == 2:
        return timedelta(minutes=parts[0], seconds=parts[1])
    if len(parts) == 3:
        return timedelta(hours=parts[0], minutes=parts[1], seconds=parts[2])
    raise ValueError(f"Unsupported finish time: {value}")


def match_teams(rows: list[dict], sex: str) -> list[dict]:
    team_aliases = common_team_names | (
        male_team_names if sex == "M" else female_team_names
    )
    teams = list(Team.objects.all())
    for row in rows:
        canonical = row["raw_team"]
        for alias, name in team_aliases.items():
            if alias.casefold() == canonical.casefold():
                canonical = name
                break
        team_matches = [
            team
            for team in teams
            if team.full_name.casefold() == canonical.casefold()
            or team.short_name.casefold() == canonical.casefold()
        ]
        row["teams"] = [
            {"id": team.id, "name": team.full_name} for team in team_matches
        ]
    return rows
