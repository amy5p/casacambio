from django.shortcuts import render
from django.utils.html import format_html
from django.views.generic import TemplateView, ListView, DetailView, CreateView, DeleteView, UpdateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from dal import autocomplete
from .models import *
from fuente import utils
from fuente.var import *






class PersonaListView(LoginRequiredMixin, ListView):
    """
    Listado de personas.
    """
    model = Persona

    @utils.context_decorator()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    @utils.queryset_decorator()
    def get_queryset(self, request):
        return super().get_queryset(request)


class PersonaDetailView(LoginRequiredMixin, DetailView):
    """
    Detalle de una persona.
    """
    model = Persona

    @utils.context_decorator()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class PersonaCreateView(LoginRequiredMixin, CreateView):
    """
    Crea una persona.
    """
    model = Persona
    fields = "__all__"

    @utils.context_decorator()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class PersonaUpdateView(LoginRequiredMixin, UpdateView):
    """
    Modifica una persona.
    """
    model = Persona
    fields = "__all__"

    @utils.context_decorator()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context



# -----------------------------------------------------------------------
# django-autocomplete-light ---------------------------------------------
# -----------------------------------------------------------------------

class PersonaAutocomplete(autocomplete.Select2QuerySetView, utils.Texto):
    model = Persona

    def get_queryset(self):
        # ¡No olvides filtrar los resultados dependiendo del visitante!
        if not self.request.user.is_authenticated:
            return self.model.objects.none()

        qs = self.model.objects.all()

        if self.q:
            q = self.GetEtiqueta(self.q, False)
            qs = qs.filter(tags__icontains=q)

        return qs




