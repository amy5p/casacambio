from django.urls import path
from .views import *


urlpatterns = [
    path("documento/list/", DocumentoListView.as_view(), name="documento-documento-list"),
    path("documento/list/<int:pk>/", DocumentoDetailView.as_view(), name="documento-documento-detail"),
    path("documento/list/<int:pk>/print/", DocumentoPrintDetailView.as_view(), name="documento-documento-print"),
    path("documento/create/", DocumentoCreateView.as_view(), name="documento-documento-create"),
    path("documento/factura/create/", DocumentoFacturaCreateView.as_view(), name="documento-documento-factura-create"),
    path("documento/entrada/create/", DocumentoEntradaCreateView.as_view(), name="documento-documento-entrada-create"),
    path("documento/salida/create/", DocumentoSalidaCreateView.as_view(), name="documento-documento-salida-create"),


    # Json views
    path("documento/json/calcular/monto-salida/", documentoCalcularMontoSalida, name="documento-documento-json-calcular-monto-salida"),
    path("documento/json/calcular/monto-entrada/", documentoCalcularMontoEntrada, name="documento-documento-json-calcular-monto-entrada"),


]




