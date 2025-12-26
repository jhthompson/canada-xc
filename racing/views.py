from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from racing.models import Conference, Meet, Race, RosterSpot, Runner, Team


def index(request, conference_short_name=None):
    if conference_short_name:
        latest_results = Race.objects.filter(
            meet__conference__short_name=conference_short_name
        ).order_by("-meet__date")[:2]
        upcoming_meets = Meet.objects.filter(
            conference__short_name=conference_short_name, date__gt=timezone.now()
        )
    else:
        latest_results = Race.objects.all().order_by("-meet__date")[:2]
        upcoming_meets = Meet.objects.filter(date__gt=timezone.now())

    return render(
        request,
        "racing/index.html",
        {
            "latest_results": latest_results,
            "upcoming_meets": upcoming_meets,
        },
    )
    
def about(request):
    return render(request, "racing/about.html")


def meet(request, year: int, slug: str):
    meet = get_object_or_404(Meet, date__year=year, slug=slug)

    return render(request, "racing/meet.html", {"meet": meet})


def race(request, year: int, slug: str, race_info: tuple[int, str, str]):
    meet = get_object_or_404(Meet, date__year=year, slug=slug)

    distance, unit, sex = race_info
    race = get_object_or_404(Race, meet=meet, distance=distance, unit=unit, sex=sex)

    # For each result, attach the roster spot (for headshot)
    results = []
    top_results = race.top_results().select_related("runner", "team")
    roster_spots = RosterSpot.objects.filter(
        runner__in=[result.runner for result in top_results],
        team__in=[result.team for result in top_results],
        year=race.meet.date.year,
    )

    roster_spot_dict = {(spot.runner_id, spot.team_id): spot for spot in roster_spots}

    for result in top_results:
        result.roster_spot = roster_spot_dict.get((result.runner_id, result.team_id))
        results.append(result)

    return render(request, "racing/race.html", {"race": race, "results": results})


def runners(request):
    name = request.GET.get("name")

    if name:
        runners = Runner.objects.filter(name__icontains=name).order_by("name").all()
    else:
        runners = Runner.objects.none()

    if request.htmx:
        template = "racing/partials/runners_list.html"
    else:
        template = "racing/runners.html"

    return render(request, template, {"runners": runners})


def runner(request, slug):
    runner = get_object_or_404(Runner, slug=slug)

    # Get runner's results
    results_with_positions = []
    for result in runner.result_set.all():
        # Get all results from this race ordered by time
        race_results = result.race.top_results()
        # Find position of current result
        position = list(race_results).index(result) + 1
        # Store result and position
        results_with_positions.append(
            {
                "result": result,
                "position": position,
            }
        )

    # Sort by date descending
    results_with_positions.sort(key=lambda x: x["result"].race.meet.date, reverse=True)

    context = {"runner": runner, "results": results_with_positions}

    head_to_head_slug = request.GET.get("head-to-head")
    context = context | get_head_to_head_context(runner.slug, head_to_head_slug)

    if request.htmx:
        return render(request, "racing/partials/head_to_head.html", context)
    else:
        return render(request, "racing/runner.html", context)


def get_head_to_head_context(slug_a: str, slug_b: str):
    a = get_object_or_404(Runner, slug=slug_a)
    try:
        b = Runner.objects.get(slug=slug_b)
    except Runner.DoesNotExist:
        return {
            "runnerA": a,
            "runnerB": None,
            "common_races": [],
            "wins_a": 0,
            "wins_b": 0,
            "all_runners": Runner.objects.filter(sex=a.sex),
        }

    # Get all results for each runner
    resultsA = a.result_set.all()
    resultsB = b.result_set.all()

    # Find common races between the two result sets
    common_races = []
    for resultA in resultsA:
        resultB = resultsB.filter(race=resultA.race).first()
        if resultB:
            common_races.append(
                {
                    "race": resultA.race,
                    "meet": resultA.race.meet,
                    "runnerA": {
                        "time": resultA.time,
                        "position": list(resultA.race.top_results()).index(resultA) + 1,
                    },
                    "runnerB": {
                        "time": resultB.time,
                        "position": list(resultB.race.top_results()).index(resultB) + 1,
                    },
                    "time_diff": abs(resultA.time - resultB.time),
                }
            )

    # Sort by date descending
    common_races.sort(key=lambda x: x["meet"].date, reverse=True)

    # Calculate win totals
    wins_a = sum(
        1 for race in common_races if race["runnerA"]["time"] < race["runnerB"]["time"]
    )
    wins_b = sum(
        1 for race in common_races if race["runnerB"]["time"] < race["runnerA"]["time"]
    )

    return {
        "runnerA": a,
        "runnerB": b,
        "common_races": common_races,
        "wins_a": wins_a,
        "wins_b": wins_b,
        "all_runners": Runner.objects.filter(sex=a.sex),
    }


def get_meet_years():
    """
    Returns a list of years when meets may have happened.
    Starts from the current year and goes back to the oldest meet's year.
    """
    oldest_meet = Meet.objects.order_by("date").first()
    current_year = timezone.now().year
    if oldest_meet:
        return list(range(oldest_meet.date.year, current_year + 1))[::-1]
    return []


def results(request):
    meets = Meet.objects.filter(date__lte=timezone.now()).order_by("-date")

    if conference_short_name := request.GET.get("conference"):
        meets = meets.filter(conferences__short_name=conference_short_name)

    if year := request.GET.get("year"):
        meets = meets.filter(date__year=year)

    if request.htmx:
        template = "racing/partials/results_list.html"
    else:
        template = "racing/results.html"

    return render(
        request,
        template,
        {
            "meets": meets,
            "conferences": Conference.objects.all(),
            "years": [str(y) for y in get_meet_years()],
            "selected_conference": conference_short_name,
            "selected_year": year,
        },
    )


def roster(request, year: int, slug: str):
    team = get_object_or_404(Team, slug=slug)

    spots = RosterSpot.objects.filter(team__slug=slug, year=year)
    males = spots.filter(runner__sex="M")
    females = spots.filter(runner__sex="F")

    return render(
        request,
        "racing/roster.html",
        {"year": year, "team": team, "males": males, "females": females},
    )


def schedule(request):
    return render(request, "racing/schedule.html")
