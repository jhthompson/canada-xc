from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from racing.models import Meet, Race, Runner


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
    
def runners(request):
    return render(request, "racing/runners.html")

def runner(request, slug):
    runner = get_object_or_404(Runner, slug=slug)
    
    return render(request, "racing/runner.html", {"runner": runner })

def results(request):
    return render(request, "racing/results.html")

def schedule(request):
    return render(request, "racing/schedule.html")
