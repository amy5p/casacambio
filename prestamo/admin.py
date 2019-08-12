from django.contrib import admin

# Register your models here.



from .models import *

admin.site.register(Prestamo)
admin.site.register(Solicitud)
admin.site.register(Transaccion)
admin.site.register(Cuenta)