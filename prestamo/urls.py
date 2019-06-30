"""company URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='prestamos'),
    
    path('solicitud/', views.SolicitudView.as_view(), name='prestamo-solicitud'),
    path('solicitud/enviada/', views.SolicitudEnviadaView.as_view(), name='prestamo-solicitud-enviada'),
    path('calculadora/', views.CalculadoraView.as_view(), name='prestamo-calculadora'),
    path('prestamo/list/', views.PrestamoListView.as_view(), name='prestamo-prestamo-list'),
    path('prestamo/list/<int:pk>/', views.PrestamoDetailView.as_view(), name='prestamo-prestamo-detail'),
    path('prestamo/list/<int:pk>/update/', views.PrestamoUpdateView.as_view(), name='prestamo-prestamo-update'),
    path('prestamo/list/<int:pk>/desembolsar/', views.desembolsar_view, name='prestamo-prestamo-desembolsar'),
    path('prestamo/list/<int:pk>/pagar/', views.pagar_view, name='prestamo-prestamo-pagar'),
    path('prestamo/list/<int:pk>/print/', views.print_view, name='prestamo-prestamo-print'),
    path('prestamo/create/', views.PrestamoCreateView.as_view(), name='prestamo-prestamo-create'),
    path('prestamo/stat/', views.PrestamoStatView.as_view(), name="prestamo-prestamo-estadisticas"),

    path("transaccion/list/<int:pk>/", views.TransaccionDetailView.as_view(), name="prestamo-transaccion-detail"),
    path("transaccion/create/", views.TransaccionCreateView.as_view(), name="prestamo-transaccion-create"),

    path("cuenta/list/<int:pk>/", views.CuentaDetailView.as_view(), name="prestamo-cuenta-detail"),


    # JSON
    path("cuenta/json/list/", views.CuentaAutocomplete.as_view(), name="prestamo-cuenta-json-list"),
]
