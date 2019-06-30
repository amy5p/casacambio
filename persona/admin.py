from django.contrib import admin
from .models import *



for model in [Persona]:
    admin.site.register(model)