from django.shortcuts import render
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.core.exceptions import FieldError, ObjectDoesNotExist
from django.views.generic import TemplateView, ListView, DetailView, DeleteView, FormView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from dal import autocomplete
# Locales
from .models import *
from fuente import utils
from fuente.var import *





class AlmacenListView(LoginRequiredMixin, ListView):
    """
    Listado de almacén.
    """
    model = Almacen

    @utils.context_decorator()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context



class AlmacenUpdateView(LoginRequiredMixin, UpdateView):
    """
    Actualizar almacén.
    """
    model = Almacen
    fields = "__all__"

    @utils.context_decorator()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    







# ---------------------------------------------------
# AUTOCOMPLETE LIGHT
# ---------------------------------------------------

class AlmacenAutocomplete(autocomplete.Select2QuerySetView, utils.Texto):

    def get_queryset(self):
        # ¡No olvides filtrar los resultados dependiendo del visitante!
        if not self.request.user.is_authenticated:
            return Almacen.objects.none()

        qs = Almacen.objects.all()

        if self.q:
            q = self.GetEtiqueta(self.q, False)
            qs = qs.filter(tags__icontains=q)

        return qs