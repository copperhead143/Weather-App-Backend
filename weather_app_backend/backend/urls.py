from django.urls import path
from . import views

urlpatterns = [
    path('forecast/', views.WeatherForecastView.as_View(), name='forecast'),
    
]