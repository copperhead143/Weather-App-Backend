from django.shortcuts import render
from rest_framework import status
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
# Create your views here.
class WeatherForecastView(APIView):
    def get(self, request):
        try:
            latitude = request.query_params.get('latitude')
            longitude = request.query_params.get('longitude')

            #wyrzucenie błędu gdy nie zostaną podane współrzędne
            if not latitude or longitude:
                return Response({
                    'error': 'Latiture and logitude are required parameters'
                },status=status.HTTP_400_BAD_REQUEST)
            
            try:
                lat=float(latitude)
                lon=float(longitude)

                #sprawdzenie warunków koordynatów geograficznych
                #szerokość (północ-południe)
                if not (-90 <= lat <= 90):
                    return Response({
                        'error': 'Latitude must be between -90 and 90'
                    },status=status.HTTP_400_BAD_REQUEST)
                
                #dlugosc (wschód-zachód)
                if not (-180 <= lon <= 180):
                    return Response ({
                        'error': 'Longitude must be between -180 and 180'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
            except ValueError:
                return Response({
                    'error': 'Given longitude or latitude is not a valid number'
                })
            
            url = "https://api.open-meteo.com/v1/forecast" #podpatrzone z open-meteo.com/en/docs
            params = { #definicja parametrow, które chcemy od api zgodnie z jego dokumentacja
                'latitude' : lat,
                'longitude': lon,
                'daily' : 'weathercode,temperature_2m_max,temperature_2m_min,sunshine_duration', #kod pogody, temperatura max, temperratura min, czas swiecenia slonca
                'timezone' : 'auto',
                'forecast_days': 7
            }

            response = requests.get(url, params)


            