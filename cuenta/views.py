from django.shortcuts import render
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.core.exceptions import FieldError, ObjectDoesNotExist
from django.views.generic import TemplateView, ListView, DetailView, DeleteView, FormView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

# Locales
from almacen.models import Almacen
from .models import *
from fuente import utils



# --------------------------------------------------------------
# CUENTAS
# --------------------------------------------------------------


class CuentaListView(LoginRequiredMixin, ListView, utils.Texto):
    """
    Listado de cuentas.
    """
    model = Cuenta

    @utils.context_decorator()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    @utils.queryset_decorator()
    def get_queryset(self):
        pass


class CuentaDetailView(LoginRequiredMixin, DetailView, utils.Texto):
    """
    Detalle de una cuenta.
    """
    model = Cuenta

    @utils.context_decorator()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class CuentaCreateView(LoginRequiredMixin, CreateView):
    """
    Crea una cuenta.
    """
    model = Cuenta
    fields = "__all__"

    @utils.context_decorator()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class CuentaUpdateView(LoginRequiredMixin, UpdateView):
    """
    Modifica una cuenta.
    """
    model = Cuenta
    fields = "__all__"

    @utils.context_decorator()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


# ---------------------------------------------------
# JSON VIEWS 
# ---------------------------------------------------

utilst = utils.Texto()

@login_required()
def cuentaDetailJson(request):
    """
    Un único objecto.
    :param request:
    :return: JsonResponse({})
    """
    pk = request.GET.get("id")
    try:
        obj = Cuenta.objects.get(id=pk)
    except (ObjectDoesNotExist, ValueError):
        return JsonResponse({"results": None, "error": True,
                             "message": _("No existen {} con el id '{}'".format(Cuenta._meta.verbose_name_plural, pk))})

    detail = utils.Detail(obj, subfields="__all__")
    return JsonResponse({"results": detail.GetFieldsAndValuesJson(), "error": False, "message": ""})

@login_required()
def cuentaListJson(request):
    """
    Listado de objetos.
    :param request:
    :return: JsonResponse({})
    """
    qs = Cuenta.objects.all()

    q = request.GET.get("q")
    almacenid = request.GET.get("almacenid")

    if q:
        q = utilst.GetEtiqueta(q, False)
        qs = qs.filter(tags__icontains=q)

    if almacenid:
        qs = qs.filter(almacen_id=almacenid)

    data = [{"id": obj.id, "name": str(obj), "orden": obj.orden} for obj in qs]

    almacen = Almacen.objects.get(id=almacenid)
    return JsonResponse({"results": data, "error": False, "message": ""})

@login_required()
def cuentaTasaListJson(request):
    """
    Obtiene un diccionario de las diferentes tasas de todas 
    las cuentas y su clave será el id de dicha cuenta.
    """
    qs = Cuenta.objects.all()

    data = dict()
    for obj in qs:
        data[obj.id] = {"compra": obj.moneda.tasa_compra, "venta": obj.moneda.tasa_venta}

    return JsonResponse({"results": data, "error": False, "message": ""})


@login_required()
def cuentaPredeterminadaJson(request):
    """
    Obtiene los datos de la cuenta predeterminada.
    """
    try:
        obj = Cuenta.objects.get(moneda__is_principal = True)
    except (ObjectDoesNotExist):
        return JsonResponse({"results": None, "error": True, "message": _("No existe una moneda predeterminada.")})

    detail = utils.Detail(obj, subfields=None)
    return JsonResponse({"results": detail.GetFieldsAndValuesJson(), "error": False, "message": ""})
    
