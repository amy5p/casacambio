from django.urls import path
from .views import *


urlpatterns = [
    path("almacen/list/", AlmacenListView.as_view(), name="almacen-almacen-list"),
    path("almacen/list/<int:pk>/update/", AlmacenUpdateView.as_view(), name="almacen-almacen-update"),
    



]




