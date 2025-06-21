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


            if response.status_code != 200:
                return Response ({
                    'error': 'faild to fetch data from open-meteo'
                }, status=status.HTTP_502_BAD_GATEWAY)
            
            weather_data = response.json()
            
            if 'daily' not in weather_data:
                return Response({
                    'error': 'invalid response from API'
                }, status=status.HTTP_502_BAD_GATEWAY)
            
            #obliczanie szacowanej wygenerowanej energii w kWh

            SOLAR_FARM_POWER_KW = 2.5 #moc instalacji w kW
            FARM_EFFICIENCY = 0.2 #sprawność instalacji

            #przetworzenie danych w celu uzyskania prognozy na 7 dni
            forecast_data = []
            daily_data = weather_data['daily']

            for i in range(7):
                date = daily_data['time'][i]
                weather_code = daily_data['weathercode'][i]
                temp_max = daily_data['temperature_2m_max'][i]
                temp_min = daily_data['temperature_2m_min'][i]
                sunshine_time_seconds = daily_data['sunshine_duration'][i] #api zwraca w sekundach

                sunshine_time_hours = sunshine_time_seconds / 3600

                #obliczenie enegrii wygenerowanej
                #jak w treści zadania
                #energy[kWh] = moc[kW] x czas[h] x sprawność
                energy_generated = SOLAR_FARM_POWER_KW * sunshine_time_hours * FARM_EFFICIENCY

                forecast_data.append({
                    'date': date,
                    'weather_code': weather_code,
                    'temperature_max': temp_max,
                    'temperature_min': temp_min,
                    'gen_energry_kWh': energy_generated,
                    'sunshine_time_hours': round(sunshine_time_hours,2)
                })

            return Response({
                'forecast': forecast_data,
                'location': {
                    'latitude': lat,
                    'longitude': lon
                }
            })

        except requests.RequestExcetption:
            return Response ({
                'error': 'failed connection to weather servie'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        except Exception as e:
            return Response({
                'error': 'Internal server error'
            }, status=status.status.HTTP_500_INTERNAL_SERVER_ERROR)