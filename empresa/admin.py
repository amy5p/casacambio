from django.contrib import admin
from .models import *



for model in [Empresa]:
    admin.site.register(model)



