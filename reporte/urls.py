from django.urls import path
from .views import *


urlpatterns = [
    path("reporte/", ReporteView.as_view(), name="reporte-reporte"),
    path("reporte/dia/", ReporteDiaView.as_view(), name="reporte-reporte-dia"),
    path("reporte/mes/", ReporteMesView.as_view(), name="reporte-reporte-mes"),
    path("reporte/ano/", ReporteAnoView.as_view(), name="reporte-reporte-ano"),

    path("reporte/export/csv/reporte.csv", reporteExportToCSV, name="reporte-reporte-export-csv"),



]




