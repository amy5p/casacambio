from django.shortcuts import render
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.core.exceptions import FieldError, ObjectDoesNotExist
from django.utils.translation import gettext as _
from django.views.generic import CreateView, DeleteView, UpdateView, TemplateView, ListView, DetailView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from fuente import utils
from .models import *
from .forms import *

utilst = utils.Texto()



class MonedaListView(LoginRequiredMixin, ListView, utils.Texto):
    """
    Listado de monedas.
    """
    model = Moneda

    @utils.context_decorator()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    @utils.queryset_decorator()
    def get_queryset(self):
        pass


class MonedaDetailView(LoginRequiredMixin, DetailView, utils.Texto):
    """
    Detalle de una moneda.
    """
    model = Moneda

    @utils.context_decorator()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class MonedaCreateView(LoginRequiredMixin, CreateView):
    """
    Crea una moneda.
    """
    model = Moneda
    fields = "__all__"

    @utils.context_decorator()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class MonedaUpdateView(LoginRequiredMixin, UpdateView):
    """
    Modifica una moneda.
    """
    model = Moneda
    fields = "__all__"

    @utils.context_decorator()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class MonedaTasasFormView(LoginRequiredMixin, CreateView):
    """
    Ajuste masivo de las tasas de todas 
    la monedas configuradas.
    """
    model = MonedaTasasUpdate
    template_name = "moneda/moneda_tasas_form.html"
    form_class = MonedaTasasForm
    success_url = reverse_lazy("moneda-moneda-list")

    @utils.context_decorator()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        dic = dict()
        objects = form.objects
        for id in objects:
            moneda = objects[id]
            moneda.save()
            dic[moneda.id] = {"id": moneda.id, "tasa_compra": moneda.tasa_compra, "tasa_venta": moneda.tasa_venta}
        form.items = str(dic)
        return super().form_valid(form)


# -----------------------------------------------------
# JSON VIEWS
# -----------------------------------------------------

def monedaDetailJson(request):
    """
    Un único objecto.
    """
    pk = request.GET.get("id")
    try:
        obj = Moneda.objects.get(id=pk)
    except (ObjectDoesNotExist, ValueError):
        return JsonResponse({"results": None, "error": True, "message": _("No existen {} con el id '{}'".format(Moneda._meta.verbose_name_plural, pk))})

    detail = utils.Detail(obj, subfields="__all__")
    return JsonResponse({"results": detail.GetFieldsAndValuesJson(), "error": False, "message": ""})



def monedaListJson(request):
    """
    Un listado de objectos.
    """
    try:
        q = request.GET["q"]
    except (KeyError):
        qs = Moneda.objects.all()
    else:
        try:
            q = utilst.GetEtiqueta(q, False)
            qs = Moneda.objects.filter(tags__icontains=q)
        except (BaseException) as e:
            return JsonResponse({"results": [], "error": True, "message": str(e)})
    
    data = [{"id": obj.id, "name": str(obj)} for obj in qs]
    return JsonResponse({"results": data, "error": False, "message": ""})