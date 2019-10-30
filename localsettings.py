"""
Archivo utilizado para establecer configuraciones locales
de este proyecto.

Este archivo no será seguido por GIT, y su objetito está en
establecer parametros que determinán parte del comportamento del
proyecto, dependiente de donde se encuentre instalado.
"""


DEBUG = True

ALLOWED_HOSTS = ["*"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'casacambio',
        'USER': 'root',
        'PASSWORD': 'HolaMundo',
        'HOST': 'localhost',
        'TEST': {
            'NAME': 'test',
        },
    }
}