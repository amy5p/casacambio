from django.contrib import admin
from .models import *



for model in [Moneda]:
    admin.site.register(model)