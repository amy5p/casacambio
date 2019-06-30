from django.urls import path
from .views import *


urlpatterns = [
    path("cuenta/list/", CuentaListView.as_view(), name="cuenta-cuenta-list"),
    path("cuenta/list/<int:pk>/", CuentaDetailView.as_view(), name="cuenta-cuenta-detail"),
    path("cuenta/list/<int:pk>/update/", CuentaUpdateView.as_view(), name="cuenta-cuenta-update"),
    path("cuenta/create/", CuentaCreateView.as_view(), name="cuenta-cuenta-create"),



    # Json views
    path("cuenta/json/list/", cuentaListJson, name="cuenta-cuenta-json-list"),
    path("cuenta/json/detail/", cuentaDetailJson, name="cuenta-cuenta-json-detail"),
    path("cuenta/json/tasas/", cuentaTasaListJson, name="cuenta-cuenta-json-tasas"),
    path("cuenta/json/predeterminada/", cuentaPredeterminadaJson, name="cuenta-cuenta-json-predeterminada"),




]




