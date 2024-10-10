
from django.urls import path

from racing.views import index

urlpatterns = [
    path('', index, name='index'),
]
