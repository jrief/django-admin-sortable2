from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'secret_key'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'adminsortable2',
    'testapp',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': Path(__file__).parent.parent / 'workdir/demo.sqlite3',
        'TEST': {
            'NAME': Path(__file__).parent.parent / 'workdir/test.sqlite3',  # live_server requires a file rather than :memory:
            'OPTIONS': {
                'timeout': 20,
            },
        },
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

USE_TZ = False

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'testapp.middleware.AutoLoginMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
]

ROOT_URLCONF = 'testapp.urls'

SILENCED_SYSTEM_CHECKS = ['admin.E408']

# URL that handles the static files served from STATIC_ROOT.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.jinja2.Jinja2',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [],
    },
}, {
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]

WSGI_APPLICATION = 'wsgi.application'
