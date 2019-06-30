from django.urls import path
from .views import *


urlpatterns = [
    path("persona/list/", PersonaListView.as_view(), name="persona-persona-list"),
    path("persona/list/<int:pk>/", PersonaDetailView.as_view(), name="persona-persona-detail"),
    path("persona/list/<int:pk>/update/", PersonaUpdateView.as_view(), name="persona-persona-update"),
    path("persona/create/", PersonaCreateView.as_view(), name="persona-persona-create"),


    # AUTOCOMPLETE-LIGHT
    path("persona/json/list/", PersonaAutocomplete.as_view(), name="persona-persona-json-list"),

]




