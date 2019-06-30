from django.contrib import admin
from .models import *





for model in [DocumentoTipo, Documento]:
    admin.site.register(model)
