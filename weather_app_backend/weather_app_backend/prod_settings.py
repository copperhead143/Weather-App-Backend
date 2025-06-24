import os
from .settings import *

DEBUG = False


SECRET_KEY = os.environ.get('SECRET_KEY')


ALLOWED_HOSTS = ['*']


STATIC_ROOT = BASE_DIR / 'staticfiles'

CORS_ALLOW_ALL_ORIGINS = True

"""CORS_ALLOWED_ORIGINS = [
    "https://your-frontend-domain.onrender.com", #url fronendu
]"""