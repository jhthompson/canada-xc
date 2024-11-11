from django.urls import path, register_converter

from racing.converters import ConferenceConverter, RaceConverter, YearConverter
from racing.views import index, meet, race, results, roster, runner

register_converter(ConferenceConverter, "conference")
register_converter(YearConverter, "year")
register_converter(RaceConverter, "race_info")

urlpatterns = [
    path("", index, name="index"),
    
    # results
    path("results/", results, name="results"),
    path('results/<int:year>/<slug:slug>/', meet, name='meet'),
    path('results/<int:year>/<slug:slug>/<race_info:race_info>', race, name='race'),
    
    # schedule
    # path("schedule/", schedule, name="schedule"),
    
    # runners
    # path('runners/', runners, name='runners'),
    path('runners/<slug:slug>/', runner, name='runner'),
    
    # teams
    # path('teams/', teams, name='teams'),
    # path('teams/<slug:slug>/', team, name='team'),
    path('teams/<slug:slug>/<year:year>/', roster, name='roster'),
    
    # per-conference URLs (mirroring the above default URLs)
    # path("<conference:conference>", index, name="conference_index")
    
    # TODO: path("conferences/", ...),
    # one path() for each conference? AUS, OUA, RSEQ, CW
    # or maybe a query parameter to filter the information?
    
    # canada-xc.ca/aus/schedule/2014
    # canada-xc.ca/schedule/2015?conference=AUS
    # 
    # maybe could be the conference URLs mirror the default ones?
    # canada-xc.ca/         <- overall home page
    # canada-xc.ca/aus/     <- AUS home page
    
    # canada-xc.ca/schedule/    <- overall schedule for all conferences
    # canada-xc.ca/aus/schedule/    <- overall schedule for AUS
]
