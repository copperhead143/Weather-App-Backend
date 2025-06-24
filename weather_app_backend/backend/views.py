from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
import statistics

class WeatherForecastView(APIView):
    def get(self, request):
        # 1) Pobranie i wstępna walidacja obecności
        latitude  = request.query_params.get('latitude')
        longitude = request.query_params.get('longitude')
        if latitude is None or longitude is None:
            return Response(
                {'error': 'Latitude and longitude are required parameters'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2) Parsowanie na float + zakresy
        try:
            lat = float(latitude)
            lon = float(longitude)
        except ValueError:
            return Response(
                {'error': 'Given latitude or longitude is not a valid number'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not (-90 <= lat <= 90):
            return Response(
                {'error': 'Latitude must be between -90 and 90'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not (-180 <= lon <= 180):
            return Response(
                {'error': 'Longitude must be between -180 and 180'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3) Request do Open-Meteo
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude':       lat,
            'longitude':      lon,
            'daily':          'weathercode,temperature_2m_max,temperature_2m_min,sunshine_duration',
            'timezone':       'auto',
            'forecast_days':  7,
        }
        try:
            external = requests.get(url, params=params, timeout=10)
        except requests.RequestException:
            return Response(
                {'error': 'Failed connection to weather service'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        if external.status_code != 200:
            return Response(
                {'error': 'Failed to fetch data from Open-Meteo'},
                status=status.HTTP_502_BAD_GATEWAY
            )

        data = external.json().get('daily')
        if not data:
            return Response(
                {'error': 'Invalid response from API'},
                status=status.HTTP_502_BAD_GATEWAY
            )

        # 4) Budujemy listę prognozy + energy calc
        SOLAR_POWER_KW = 2.5
        EFFICIENCY     = 0.2
        forecast = []
        for i in range(7):
            date    = data['time'][i]
            wcode   = data['weathercode'][i]
            tmax    = data['temperature_2m_max'][i]
            tmin    = data['temperature_2m_min'][i]
            sun_sec = data['sunshine_duration'][i]
            sun_h   = sun_sec / 3600
            energy  = SOLAR_POWER_KW * sun_h * EFFICIENCY
            forecast.append({
                'date':                  date,
                'weather_code':          wcode,
                'temperature_max':       tmax,
                'temperature_min':       tmin,
                'generated_energy_kWh':  round(energy, 2),
                'sunshine_time_hours':   round(sun_h, 2),
            })

        return Response({
            'forecast': forecast,
            'location': {'latitude': lat, 'longitude': lon}
        })


class WeatherSummaryView(APIView):
    def get(self, request):
        # 1) Pobranie i wstępna walidacja obecności
        latitude  = request.query_params.get('latitude')
        longitude = request.query_params.get('longitude')
        if latitude is None or longitude is None:
            return Response(
                {'error': 'Latitude and longitude are required parameters'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2) Parsowanie na float + zakresy
        try:
            lat = float(latitude)
            lon = float(longitude)
        except ValueError:
            return Response(
                {'error': 'Given latitude or longitude is not a valid number'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not (-90 <= lat <= 90):
            return Response(
                {'error': 'Latitude must be between -90 and 90'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not (-180 <= lon <= 180):
            return Response(
                {'error': 'Longitude must be between -180 and 180'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3) Request do Open-Meteo (hourly dla pressure, daily dla reszty)
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude':       lat,
            'longitude':      lon,
            'daily':          'weathercode,temperature_2m_max,temperature_2m_min,sunshine_duration',
            'hourly':         'surface_pressure',
            'timezone':       'auto',
            'forecast_days':  7,
        }
        try:
            external = requests.get(url, params=params, timeout=10)
        except requests.RequestException:
            return Response(
                {'error': 'Failed connection to weather service'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        if external.status_code != 200:
            return Response(
                {'error': 'Failed to fetch data from Open-Meteo'},
                status=status.HTTP_502_BAD_GATEWAY
            )

        payload = external.json()
        daily  = payload.get('daily', {})
        hourly = payload.get('hourly', {})

        # 4) Walidacja struktury
        if 'weathercode' not in daily or 'surface_pressure' not in hourly:
            return Response(
                {'error': 'Invalid response from API'},
                status=status.HTTP_502_BAD_GATEWAY
            )

        # 5) Obliczenia summary
        avg_pressure    = round(statistics.mean(hourly['surface_pressure']), 2)
        sun_hours_list  = [s/3600 for s in daily['sunshine_duration']]
        avg_sun_hours   = round(statistics.mean(sun_hours_list), 2)
        max_temp        = max(daily['temperature_2m_max'])
        min_temp        = min(daily['temperature_2m_min'])
        rainy_days      = sum(1 for c in daily['weathercode'] if 51 <= c <= 99)
        summary_text    = "with precipitation" if rainy_days >= 4 else "no precipitation"

        return Response({
            'average_pressure':       avg_pressure,
            'average_sunshine_hours': avg_sun_hours,
            'extreme_temperatures': {
                'max': max_temp,
                'min': min_temp
            },
            'weather_summary':        summary_text,
            'rainy_days_count':       rainy_days
        })
