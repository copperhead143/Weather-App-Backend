from django.urls import path
from . import views

urlpatterns = [
    path('forecast/', views.WeatherForecastView.as_View(), name='forecast'),
    path('summary/', views.WeatherSummaryView.as_View(), name='summary')
]