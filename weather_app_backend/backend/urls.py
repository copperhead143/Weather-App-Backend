from django.urls import path
from . import views

urlpatterns = [
    path('forecast/', views.WeatherForecastView.as_view(), name='forecast'),
    path('summary/', views.WeatherSummaryView.as_view(), name='summary')
]