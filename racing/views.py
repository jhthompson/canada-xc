from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from racing.models import Conference, Meet, Race, RosterSpot, Runner, Team


def index(request, conference_short_name=None):
    if conference_short_name:
        latest_results = Race.objects.filter(meet__conference__short_name=conference_short_name).order_by("-meet__date")[:2]
        upcoming_meets = Meet.objects.filter(conference__short_name=conference_short_name, date__gt=timezone.now())
    else:
        latest_results = Race.objects.all().order_by("-meet__date")[:2]
        upcoming_meets = Meet.objects.filter(date__gt=timezone.now())
        
    return render(request, "racing/index.html", {
            "latest_results": latest_results,
            "upcoming_meets": upcoming_meets,
        }
    )
    
def meet(request, year: int, slug: str):
    meet = get_object_or_404(Meet, date__year=year, slug=slug)
    
    return render(request, "racing/meet.html", {"meet": meet})

def race(request, year: int, slug: str, race_info: tuple[int, str, str]):
    meet = get_object_or_404(Meet, date__year=year, slug=slug)
    
    distance, unit, sex = race_info
    race = get_object_or_404(Race, meet=meet, distance=distance, unit=unit, sex=sex)
    
    # For each result, attach the roster spot (for headshot)
    results = []
    for result in race.top_results():
        roster_spot = RosterSpot.objects.filter(
            runner=result.runner,
            team=result.team,
            year=race.meet.date.year
        ).first()
        result.roster_spot = roster_spot
        results.append(result)
    
    return render(request, "racing/race.html", {"race": race, "results": results})
    
def runners(request):
    return render(request, "racing/runners.html")

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
        results_with_positions.append({
            'result': result,
            'position': position,
        })
    
    # Sort by date descending
    results_with_positions.sort(
        key=lambda x: x['result'].race.meet.date,
        reverse=True
    )
    
    return render(request, "racing/runner.html", {
        "runner": runner,
        "results": results_with_positions
    })

def results(request):
    meets = Meet.objects.filter(date__lte=timezone.now()).order_by("-date")
    
    if conference_short_name := request.GET.get('conference'):
        meets = meets.filter(conferences__short_name=conference_short_name)

    if request.htmx:
        template = "racing/partials/results_list.html"
    else:
        template = "racing/results.html"

    return render(request, template, {
        "meets": meets,
        "conferences": Conference.objects.all(),
        "selected_conference": conference_short_name
    })

def roster(request, year: int, slug: str):
    team = get_object_or_404(Team, slug=slug)
    
    spots = RosterSpot.objects.filter(team__slug=slug, year=year)
    males = spots.filter(runner__sex="M")
    females = spots.filter(runner__sex="F")
    
    return render(request, "racing/roster.html", {
        "year": year,
        "team": team,
        "males": males,
        "females": females
    })
    

def schedule(request):
    return render(request, "racing/schedule.html")
