
AUTHOR:
 - WILMER MARTÍNEZ
 - www.wilmermartinez.com
 - 1-829-925-9531



DEPENDENCES:
 - python 3.7 o superior.
 - django 2.2 o superior.
 - pillow
 - python-barcode
 - django-braces
 - django-autocomplete-light (dal)
 - django-simple-history






********************************************************************************
USE EL SIGUIENTE CONTENIDO PARA CREAR EL ARCHIVO 'localsettings.py' EN EL
DIRECTORIO RAIZ DE SU PROYECTO, RELLENANDOLO CON LOS DATOS DE SU PROYECTO:
********************************************************************************
"""
Archivo utilizado para establecer configuraciones locales
de este proyecto.

Este archivo no será seguido por GIT, y su objetito está en
establecer parametros que determinán parte del comportamento del
proyecto, dependiente de donde se encuentre instalado.
"""

DEBUG = False
ALLOWED_HOSTS = ["rubiera.unolet.com"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'wilmermartinez$rubiera_unolet',
        'USER': 'wilmermartinez',
        'PASSWORD': 'HolaMundo',
        'HOST': 'wilmermartinez.mysql.pythonanywhere-services.com',
        'TEST': {
            'NAME': 'wilmermartinez$test',
        },
    }
}