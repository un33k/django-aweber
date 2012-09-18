import os

DEBUG = TEMPLATE_DEBUG = True

PROJECT_NAME = "aweber"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': PROJECT_NAME.strip().split(".")[0]+"_db"
    }
}
INSTALLED_APPS = [
    'aweber',
]


