FROM python:3.13-slim

WORKDIR /app

# instalacja pipenv
RUN pip install pipenv

# kopiowanie plików dependencji
COPY Pipfile Pipfile.lock ./

# instalajca dependencji
RUN pipenv install --deploy --system

COPY . .

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBUG=0

# Przejście do katalogu projektu Django
WORKDIR /app/weather_app_backend

# Zbieranie plików statycznych
RUN python manage.py collectstatic --noinput

# Wystawienie portu
EXPOSE 8000

# Uruchomienie serwera Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "weather_app_backend.wsgi:application"]