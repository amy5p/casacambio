from django.urls import path
from .views import *


urlpatterns = [
    path("moneda/list/", MonedaListView.as_view(), name="moneda-moneda-list"),
    path("moneda/list/<int:pk>/", MonedaDetailView.as_view(), name="moneda-moneda-detail"),
    path("moneda/list/<int:pk>/update/", MonedaUpdateView.as_view(), name="moneda-moneda-update"),
    path("moneda/create/", MonedaCreateView.as_view(), name="moneda-moneda-create"),
    path("moneda/tasas/update/", MonedaTasasFormView.as_view(), name="moneda-moneda-tasas-update"),



    # Json views
    path("moneda/json/list/", monedaListJson, name="moneda-moneda-json-list"),
    path("moneda/json/detail/", monedaDetailJson, name="moneda-moneda-json-detail"),



]




