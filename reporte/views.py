import datetime
from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from fuente import utils
from fuente.var import *
from .models import *
from documento.models import Documento
from almacen.models import Almacen
from moneda.models import Moneda
from base.models import Configuracion


conf = Configuracion()




class ReporteBase(list):
    
    def toCSV(self, split=";"):
        """
        Retorna una cadana de texto con valores separados por coma o punto y coma
        según se indique.
        """
        replace = {";": ",", ",": ";", "-": "_", "_": "-"}.get(split, split)
        if len(self) == 0:
            return ""
        columns = split.join([str(key).replace(split, replace).upper() for key in self[0].keys()])
        lines = []
        for dic in self:
            lines.append(split.join([str(value).replace(split, replace) for value in dic.values()]))
        values = "\n".join(lines)
        return "{}\n{}".format(columns, values)


class ReporteDia(ReporteBase):

    def __init__(self, qs):
        dic = {}
        fechas = []
        self.total_monto = 0
        self.total_ganancia = 0
        self.total_cantidad = 0

        for obj in qs:
            item = {
                "numero": obj.numero,
                "tipo": obj.tipo.codigo,
                "almacen": obj.almacen,
                "fecha": obj.fecha_creacion,
                "cajero": obj.cajero,
                "cliente": obj.persona,
                "entrada": obj.GetEntradaString(),
                "salida": obj.GetSalidaString(),
                "tasa": obj.GetTasa(),
                "ganancia": obj.GetGanancia(),
            }
            self.append(item)

        




class ReporteMes(ReporteBase):

    def __init__(self, qs):

        dic = {}
        fechas = []
        self.total_monto = 0
        self.total_ganancia = 0
        self.total_cantidad = 0

        for obj in qs:
            try:
                dic[obj.fecha]["monto_entrada"] += obj.monto_entrada
                dic[obj.fecha]["ganancia"] += obj.ganancia
                dic[obj.fecha]["cantidad"] += 1
            except (KeyError):
                dic[obj.fecha] = {"almacen": str(obj.almacen), "moneda": obj.entrada.moneda.simbolo, "fecha": obj.fecha, "monto_entrada": obj.monto_entrada, "ganancia": obj.ganancia, "cantidad": 1}
                fechas.append(obj.fecha)

        fechas.sort()

        for fecha in fechas:
            self.append(dic[fecha])
            self.total_monto += dic[fecha]["monto_entrada"]
            self.total_ganancia += dic[fecha]["ganancia"]
            self.total_cantidad += dic[fecha]["cantidad"]



            


    
class ReporteAno(ReporteBase):

    def __init__(self, qs):

        dic = {}
        fechas = []
        self.total_monto = 0
        self.total_ganancia = 0
        self.total_cantidad = 0

        for obj in qs:
            fecha = "{}-{}".format(obj.fecha.month, obj.fecha.year)
            try:
                dic[fecha]["monto_entrada"] += obj.monto_entrada
                dic[fecha]["ganancia"] += obj.ganancia
                dic[fecha]["cantidad"] += 1
            except (KeyError):
                dic[fecha] = {"almacen": str(obj.almacen), "moneda": obj.entrada.moneda.simbolo, "fecha": fecha, "monto_entrada": obj.monto_entrada, "ganancia": obj.ganancia, "cantidad": 1}
                fechas.append(fecha)
        
        fechas.sort()

        for fecha in fechas:
            self.append(dic[fecha])
            self.total_monto += dic[fecha]["monto_entrada"]
            self.total_ganancia += dic[fecha]["ganancia"]
            self.total_cantidad += dic[fecha]["cantidad"]




class ReporteView(LoginRequiredMixin, TemplateView):
    """
    Reporte página principal.
    """
    template_name = "reporte/reporte.html"

    @utils.context_decorator()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["subtitle"] = _("REPORTES")
        context["img"] = IMG_REPORTE
        return context
    

class ReporteMesView(LoginRequiredMixin, TemplateView):
    """
    Listado de los totales para cada día del mes indicado.
    """
    template_name = "reporte/reporte_mes.html"

    @utils.context_decorator()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["subtitle"] = _("REPORTE POR MES")
        context["img"] = IMG_REPORTE
        context["reporte"] = reporte_mes_json(self.request, True)
        context["almacenes"] = Almacen.objects.all()
        context["monedas"] = Moneda.objects.all()
        return context
    

class ReporteAnoView(LoginRequiredMixin, TemplateView):
    """
    Listado de los totales para cada mes del año indicado.
    """
    template_name = "reporte/reporte_ano.html"

    @utils.context_decorator()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["subtitle"] = _("REPORTE POR AÑO")
        context["img"] = IMG_REPORTE
        context["reporte"] = reporte_ano_json(self.request, True)
        context["almacenes"] = Almacen.objects.all()
        context["monedas"] = Moneda.objects.all()
        return context


class ReporteDiaView(LoginRequiredMixin, TemplateView):
    """
    Listado de los totales para el día indicado.
    """
    template_name = "reporte/reporte_dia.html"

    @utils.context_decorator()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["subtitle"] = _("REPORTE POR DÍA")
        context["img"] = IMG_REPORTE
        context["reporte"] = reporte_dia_json(self.request, True)
        context["almacenes"] = Almacen.objects.all()
        context["monedas"] = Moneda.objects.all()
        return context




class ReporteDiaPrintView(LoginRequiredMixin, TemplateView):
    """
    Listado de los totales para el día indicado.
    """
    template_name = "reporte/reporte_dia_print.html"

    @utils.context_decorator()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["subtitle"] = _("REPORTE POR DÍA")
        context["img"] = IMG_REPORTE
        context["reporte"] = reporte_dia_json(self.request, True)
        context["almacenes"] = Almacen.objects.all()
        context["monedas"] = Moneda.objects.all()
        return context




@login_required()
def reporteExportToCSV(request):
    tipo = request.GET.get("tipo")
    split = conf.csv.caracter_division_celdas

    if (tipo.lower() == "ano"):
        reporte = reporte_ano_json(request, toCSV=True, split=split)
    elif (tipo.lower() == "mes"):
        reporte = reporte_mes_json(request, toCSV=True, split=split)
    elif (tipo.lower() == "dia"):
        reporte = reporte_dia_json(request, toCSV=True, split=split)
    else:
        reporte = ""
    
    if isinstance(reporte, JsonResponse):
        return reporte
    
    return HttpResponse(content=reporte, content_type="text/csv")



# --------------------------------------------------------------
# JSON VIEWS.
# --------------------------------------------------------------

@login_required()
def reporte_dia_json(request, notJson=False, toCSV=False, split=";"):
    """
    Obtiene el reporte del dia.
    """
    fecha = request.GET.get("fecha")
    almacen_id = request.GET.get("almacen")

    try:
        y, m, d = fecha.split("-")
        fecha = datetime.date(int(y), int(m), int(d))
    except (BaseException) as e:
        return JsonResponse({"results": None, "error": True, "message": str(e)})
    try:
        almacen_id = int(almacen_id)
    except (BaseException) as e:
        almacen_id = None

    qs = Documento.objects.filter(fecha=fecha, almacen=almacen_id)

    if (toCSV):
        return ReporteDia(qs).toCSV(split)

    if (notJson):
        return ReporteDia(qs)

    return JsonResponse({"results": ReporteDia(qs), "error": False, "message": ""})


@login_required()
def reporte_mes_json(request, notJson=False, toCSV=False, split=";"):
    """
    Obtiene el reporte del mes.
    """
    mes = request.GET.get("mes")
    ano = request.GET.get("ano")
    almacen_id = request.GET.get("almacen")
    moneda_id = request.GET.get("moneda")

    try:
        mes = int(mes)
    except (BaseException) as e:
        return JsonResponse({"results": None, "error": True, "message": str(e)})
    try:
        ano = int(ano)
    except (BaseException) as e:
        return JsonResponse({"results": None, "error": True, "message": str(e)})

    try:
        moneda_id = int(moneda_id)
    except (BaseException) as e:
        return JsonResponse({"results": None, "error": True, "message": str(e)})
    try:
        almacen_id = int(almacen_id)
    except (BaseException) as e:
        almacen_id = None


    qs = Documento.objects.filter(fecha__year=ano, fecha__month=mes, entrada__moneda=moneda_id, almacen=almacen_id)

    if (toCSV):
        return ReporteMes(qs).toCSV(split)

    if (notJson):
        return ReporteMes(qs)

    return JsonResponse({"results": ReporteMes(qs), "error": False, "message": ""})
    

@login_required()
def reporte_ano_json(request, notJson=False, toCSV=False, split=";"):
    """
    Obtiene el reporte del año.
    """
    ano = request.GET.get("ano")
    almacen_id = request.GET.get("almacen")
    moneda_id = request.GET.get("moneda")

    try:
        ano = int(ano)
    except (TypeError, ValueError) as e:
        return JsonResponse({"results": None, "error": True, "message": str(e)})

    try:
        moneda_id = int(moneda_id)
    except (TypeError, ValueError) as e:
        return JsonResponse({"results": None, "error": True, "message": str(e)})

    try:
        almacen_id = int(almacen_id)
    except (TypeError, ValueError) as e:
        almacen_id = None


    qs = Documento.objects.filter(fecha__year=ano, entrada__moneda=moneda_id, almacen=almacen_id)

    if (toCSV):
        return ReporteAno(qs).toCSV(split)

    if (notJson):
        return ReporteAno(qs)
    return JsonResponse({"results": ReporteAno(qs), "error": False, "message": ""})