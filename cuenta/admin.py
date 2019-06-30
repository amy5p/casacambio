from django.contrib import admin
from .models import *



for model in [Cuenta]:
    admin.site.register(model)