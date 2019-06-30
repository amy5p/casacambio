from django.contrib import admin
from .models import *




for model in [Almacen]:
    admin.site.register(model)
