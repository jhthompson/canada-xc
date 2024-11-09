from django.urls import path, register_converter

from racing.converters import ConferenceConverter
from racing.views import index, meet, results, runner

register_converter(ConferenceConverter, "conference")

urlpatterns = [
    path("", index, name="index"),
    path("results/", results, name="results"),
    path('results/<int:year>/<slug:slug>', meet, name='meet'),
    
    # canadaxc.ca/results/2024/aus-championships
    # path("schedule/", schedule, name="schedule"),
    
    # runners
    # path('runners/', runners, name='runners'),
    path('runners/<slug:slug>/', runner, name='runner'),
    
    # per-conference URLs (mirroring the above default URLs)
    # path("<conference:conference>", index, name="conference_index")
    
    # TODO: path("conferences/", ...),
    # one path() for each conference? AUS, OUA, RSEQ, CW
    # or maybe a query parameter to filter the information?
    
    # canada-xc.ca/AUS/schedule/2014
    # canada-xc.ca/schedule/2015?conference=AUS
    # 
    # maybe could be the conference URLs mirror the default ones?
    # canada-xc.ca/         <- overall home page
    # canada-xc.ca/AUS/     <- AUS home page
    
    # canada-xc.ca/schedule/    <- overall schedule for all conferences
    # canada-xc.ca/AUS/schedule/    <- overall schedule for AUS
]
