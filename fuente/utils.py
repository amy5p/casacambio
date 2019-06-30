import sys
import datetime
import unicodedata
import itertools
from decimal import Decimal
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy, reverse, NoReverseMatch
from django.db import models
import django.views.generic
from django.db import models
# Locales
from .var import *
from . import encriptado
from . import email








class Error(BaseException):
    """
    Error personalizado del proyecto.
    """
    def __init__(self, exception=None, message="", title=""):
        self.exception = exception
        if (not message) and (self.exception):
            try:
                message = str(self.exception)
            except (Exception):
                pass
        self.message = _(message)
        self.title = "{} ({})".format(_(title), type(self.exception).__name__)
        try:
            self.message_internal = str(self.exception)
        except (Exception):
            self.message_internal = ""

        self.exc_type, self.exc_obj, self.exc_tb = sys.exc_info()
        self.fname = self.exc_tb.tb_frame.f_code.co_filename
        

    def __str__(self):
        return "{}\n{}\nMódulo: {}, línea: {}\n{}\n{}".format(self.title, self.exc_type, self.fname, self.exc_tb.tb_lineno, self.message, self.message_internal)







def get_pk_from_url(url):
    """
    Obtiene el valor 'pk' de la url.
    """
    parts = url.split("/")
    for part in parts:
        try:
            return int(part)
        except (TypeError, ValueError):
            continue 
    return None



def queryset_decorator(*args, **kwargs):
    """
    Decorador para el método get_queryset en las 
    clases basadas en vistas django.
    """
    def get_queryset_decorator(f):

        def new_function(self):
            try:
                q = self.request.GET["q"]
            except (KeyError):
                return self.model.objects.all()

            return self.model.objects.filter(tags__icontains=q)
        
        return new_function
    return get_queryset_decorator



def context_decorator(*args, **kwargs):
    """
    Decorador para el método get_context_data en las 
    clases basadas en vistas de django.
    """
    menus = []
    mlist = Menu("list", "Listado", "", IMG_LIST, False, "Ir al listado")
    mcreate = Menu("create", "Nuevo", "", IMG_ADD, False, "Crear un nuevo registro")
    mupdate = Menu("update", "Modificar", "", IMG_EDIT, False, "Modificar este registro")
    mdelete = Menu("delete", "Eliminar", "", IMG_DELETE, False, "Eliminar este registro")

    def get_context_decorator(f):
        def new_function(*args, **kwargs):

            context = f(*args, **kwargs)
            view = context["view"]

            if (isinstance(view, django.views.generic.DetailView)):
                menus = [mlist, mcreate, mupdate, mdelete]
            elif (isinstance(view, django.views.generic.ListView)):
                menus = [mcreate]
            elif (isinstance(view, django.views.generic.CreateView)):
                menus = [mlist]
            elif (isinstance(view, django.views.generic.UpdateView)):
                menus = [mlist, mcreate, mdelete]
            elif (isinstance(view, django.views.generic.DeleteView)):
                menus = [mlist, mcreate, mupdate]
            else:
                menus = [mlist]
            
            try:
                modelname = view.model.__name__.lower()
                appname = view.model.__dict__["__module__"].split(".")[0]
            except (AttributeError):
                modelname = ""
                appname = ""
            preurl = "{}-{}".format(appname, modelname)

            kwargs["submenu"] = []
            for menu in menus:
                try:
                    menu.url = reverse("{}-{}".format(preurl, menu.id).lower(), kwargs={"pk": get_pk_from_url(view.__dict__["request"].path)})
                except (NoReverseMatch) as e:
                    try:
                        menu.url = reverse("{}-{}".format(preurl, menu.id).lower())
                    except (NoReverseMatch) as e:
                        continue 
                kwargs["submenu"].append(menu)


            # Agregamos los menus que configuramos en el context_procesor
            from base.context_processors import m
            m = dict(m)
            t = "{}s".format(modelname.lower())
            try:
                menus = m[t][1]
            except (KeyError, IndexError):
                pass
            else:
                for menu in menus:
                    kwargs["submenu"].append(menu)



            # Otras opciones disponibles en las plantillas.
            kwargs["today"] = datetime.datetime.today()



            return f(*args, **kwargs)
        return new_function
    return get_context_decorator






class Field(dict):

    field = ""
    name = ""
    value = ""
    display = ""
    html = ""
    help = ""
    img = ""

    def __init__(self, data={}):
        if (data):
            for key in data:
                self.__dict__[key] = data[key]
                self[key] = data[key]

    def __str__(self):
        return str(self.display)

    def __setattr__(self, name, value):
        self.__dict__[name] = value 
        self[name] = value

    def __float__(self):
        return float(self.value)

    def __int__(self):
        return int(self.value)
    
    def __decimal__(self):
        return Decimal(self.value)
    




class Detail(object):
    """
    Facilita mostrar la información de un objeto modelo 
    cualquiera, mostrando sus fields y values. 
    """
    def __init__(self, obj=None, subfields=False):
        self.fields = []
        if (obj):
            self.GetModelDetail(obj, subfields)

    def __str__(self):
        return "{}({})".format(_("Detalle"), len(self.fields))

    def __repr__(self):
        return str(self)

    def __iter__(self):
        for field in self.fields:
            yield getattr(self, field)

    def __len__(self):
        return len(self.fields)

    def __getattr__(self, name):
        # Hacemos que si no existe la field deseada, el sistema 
        # retorne una field vacia.
        try:
            return self.__dict__[name]
        except (KeyError):
            return Field()

    def Add(self, field, name, value, display=None, html=None, help="", img=None, no_nulos=True):
        """Agrega miembros al display.
        field: El nombre de la columna en la base de datos (no necesariamente el mismo nombre).
        name: El nombre de la columna como quiere que se muestre al usuario.
        value: El valor del miembro.
        display: El valor como quiere que se muestre al usuario (opcional).
        html: Un texto con formato HTML que se usará para mostrar el valor en vez de 'value' o 'display' (opcional).
        help: Un texto que se usará como tooltips para el usuario (opcional).
        img: url de la imagen (opcional).
        """
        if (no_nulos == True):
            if (value == None) or (value == ""): # Si el valor es None o vacio, no se agrega
                return
        if display == None:
            if (isinstance(value, (float, Decimal, models.DecimalField, models.FloatField))):
                display = "{:,.2f}".format(value)
            elif (isinstance(value, datetime.date)):
                display = date.strftime("%d/%m/%Y")
            elif (isinstance(value, datetime.datetime)):
                display = value.strftime("%d/%m/%Y %H:%M")
            else:
                display = value 
            
        if html == None:
            html = display
        v = Field({"field": field, "name": _(name), "value": value, "display": display, "html": html, "help": help, "img": img})
        setattr(self, field, v)
        self.fields.append(field)

    def GetValues(self):
        values = []
        for field in self.fields:
            dic = getattr(self, field)
            values.append(dic.values())
        return values

    def GetNames(self):
        names = []
        for field in self.fields:
            dic = getattr(self, field)
            names.append(dic.get("name"))
        return names

    def GetFieldNames(self):
        return self.fields

    def GetFieldsAndValues(self):
        out = []
        for name in self.GetFieldNames():
            field = getattr(self, name)
            out.append((name, field))
        return out

    def GetFieldsAndValuesJson(self):
        out = []
        l = self.GetFieldsAndValues()
        for item in l:
            name = item[0]
            field = item[1]
        
            try:
                field["value"].pk
            except (AttributeError):
                pass 
            else:
                field["value"] = field["value"].pk 

            field["value"] = str(field["value"])

            out.append((name, field))
            print(name)
        return dict(out)

    def GetModelDetail(self, obj, subfields=False):
        """
        Obtiene el detalle automáticamente desde el 
        objecto modelo indicado.

        Si subfields es True, tambien incluye las fields de las relaciones como:
        -- field__subfield

        Si subfields es '__all__', obtiene todos las fields de las relaciones y tambien las de las
        relaciones de estas, etc. Por ejemplo:

        -- field__subfield__subfield2__subfield3__...
        """

        for field in obj._meta.get_fields():
            if (field.name in ("tags")):
                continue 
            
            try:
                field.verbose_name
            except (AttributeError):
                continue 
            
            value = getattr(obj, field.name, None)
            pk = value 
            # Si la field es una relación a otro modelo, la field
            # tendrá el valor del pk de dicho modelo, y se creará 
            # una field adicional con el formato fieldname__fieldname
            # para cada field del modelo relacionado.
            if (getattr(value.__class__, "pk", False)):

                pk = value.pk 
                value_show = "{} - {}".format(pk, value)
                
                # Agregamos todas las fields de la relación con el 
                # nombre fieldname__fieldname
                if (subfields == True):
                    try:
                        subdetail = value.GetDetail(subfields=False)
                    except (AttributeError):
                        subdetail = Detail(value)
                    for fn in subdetail:
                        self.Add("{}__{}".format(field.name, fn["field"]), "{} - {}".format(field.verbose_name, fn["name"]), fn["value"], fn["display"], fn["html"], fn["help"], fn["img"])
                
                elif (subfields == "__all__"):
                    try:
                        subdetail = value.GetDetail(subfields="__all__")
                    except (AttributeError):
                        subdetail = Detail(value)
                    for fn in subdetail:
                        self.Add("{}__{}".format(field.name, fn["field"]), "{} - {}".format(field.verbose_name, fn["name"]), fn["value"], fn["display"], fn["html"], fn["help"], fn["img"])

            elif (value is True):
                value_show = _("Si")
            elif (value is False):
                value_show = _("No")
            elif (value is None):
                value_show = ""
            elif (field.choices):
                try:
                    value_show = dict(field.choices)[value]
                except (KeyError):
                    value_show = ""
            elif (isinstance(value, datetime.datetime)):
                value_show = value.strftime("%d/%m/%Y %H:%M")
            elif (isinstance(value, datetime.date)):
                value_show = value.strftime("%d/%m/%Y")
            else:
                value_show = str(value)

            try:
                img = value.GetImg()
            except (BaseException):
                img = None

            self.Add(field.name, field.verbose_name, value, value_show, None, field.help_text, img, no_nulos=False)

        
            




class Menu(object):
    """
    Crea objetos que se utilizan como menus en las plantillas.
    """
    def __init__(self, id, name, url="", img="", selected=False, help=""):
        self.id = id
        self.name = _(name)
        self.url = url
        self.img = img
        self.selected = selected
        self.help = _(help)
        if selected == False:
            self.cssclass = "menu-item"
        else:
            self.cssclass = "menu-item menu-item-selected"

    def __str__(self):
        return str(self.name)
    
    def Html(self):
        if self.img:
            if self.selected == False:
                return '<a class="{cssclass}" id="{id}" href="{url}" title="{help}"><img class="menu-item-img" src="{img}"/>{name}</a>'.format(cssclass=self.cssclass, id=self.id, url=self.url, help=self.help, img=self.img, name=self.name)
            return '<a class="{cssclass}" id="{id}" href="{url}" title="{help}"><img class="menu-item-img" src="{img}"/>{name}</a>'.format(cssclass=self.cssclass, id=self.id, url=self.url, help=self.help, img=self.img, name=self.name)
        else:
            if self.selected == False:
                return '<a class="{cssclass}" id="{id}" href="{url}" title="{help}"><span>{name}</span></a>'.format(cssclass=self.cssclass, id=self.id, url=self.url, help=self.help, name=self.name)
            return '<a class="{cssclass}" id="{id}" href="{url}" title="{help}"><span>{name}</span></a>'.format(cssclass=self.cssclass, id=self.id, url=self.url, help=self.help, name=self.name)

    def Selected(self, state=True):
        self.selected = state 
    
    def Deselected(self, state=False):
        self.selected = state 




class Texto(object):
    """
    Clase para trabajar con textos.
    """

    def Normalize(self, string, lower=True):
        """
        remplaza el texto por uno similiar sin tíldes ni caracteres especiales como eñes, 
        ni espacios extras, y en minuscula si es indicado.
        """
        out = ''.join((c for c in unicodedata.normalize('NFD', string) if unicodedata.category(c) != 'Mn'))
        out = out.replace("  ", " ").strip()
        if lower:
            out = out.lower()
        return out

    def GetEtiqueta(self, texto, combinaciones=True):
        """
        Obtiene una cadena de texto a partir del texto indicado. Este texto
        es formateado eliminando las tildes y todos en minusculas, separados por un espacio.
        Si el parámetro combibnaciones es True, obtiene una cadena mucho más larga ya que este 
        crea multiples combinaciones para el texto resultante.
        """
        t = self.Normalize(texto, lower=True)
        if (combinaciones == True):
            return self.GetCombinaciones(t).strip()
        return t
        
    def GetEtiquetas(self, lista, combinaciones=True):
        """
        Obtiene una cadena de texto a partir de los valores de una lista. Estos valores
        son formateados eliminando las tildes y todos en minusculas, separados por un espacio.
        Si el parámetro combibnaciones es True, obtiene una cadena mucho más larga ya que este 
        crea multiples combinaciones para el texto resultante.
        """
        out = ""
        for item in lista:
            if isinstance(item, (list, tuple)):
                item = self.GetEtiquetas(item)
            item = self.Normalize(str(item))
            out += " " + item

        if (combinaciones == True):
            out = self.GetCombinaciones(out)

        return out.strip()

    def FormatForUsername(self, string, remplace="", lower=True):
        """ 
        Formatea el texto dejando solo los caracteres que esten en el rango de la 'a' a la 'z' 
        en minuzculas o mayusculas (sin la ñ ni vocales acentuadas) y los números del 1 al 9.
        Si se indica el remplace, se remplazan los caracteres no permitidos por el indicado. de lo 
        contrario se eliminará
        """
        if not remplace:
            remplace = ""
        permited = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXY0123456789"
        out = ""
        for char in string:
            if not char in permited:
                char = remplace
            out += char 
        if lower:
            return out.lower()
        return out

    def GetCombinaciones(self, arg, split=" "):
        """
        Obtiene todas las combinaciones
        posibles de la cadeda o el array pasado como parametro. Si es una cadena,
        se tomará en cuenta el argumento split que de forma predeterminada es un espacio en blanco,
        que indica donde se dividirá la cadena.

        ejemplo con el cadena: 'wilmer morel martinez' -->
        'wilmer morel wilmer martinez morel wilmer morel martinez martinez wilmer martinez morel'
        """
        text = arg
        arg = arg.split(split)
        if len(arg) < 2:
            arg += [" ", " "]
        try:
            comb = list(itertools.combinations(arg, 2))
        except (MemoryError) as e:
            arg = arg[0:len(arg)]
            return self.GetCombinaciones(arg, split=split)
            
        l = [" ".join(item) for item in comb]
        l.append(text)
        l2 = [item.replace(",", "").replace(";", "").replace(".", "").replace("-", "").replace("_", "") for item in l]
        l += l2
        return " ".join(l)

    def IsPossibleName(self, text):
        """
        Comprueba si el texto indicado puede ser un nombre, siempre y
        cuando el texto no contenga números.
        """
        numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        for n in numbers:
            if str(n) in text:
                return False
        return True

    def IsPossibleFullName(self, text):
        """
        Comprueba si el texto indicado puede ser un nombre completo,
        siempre y cuando no existan números en su contenido y exista por
        lo menos una separación con espacio.
        """
        if len(text.split(" ")) < 2:
            return False
        return self.IsPossibleName(text)

    def SetMoneda(self, numero, simbolo="$", ndec=2):
        """
        Convierte el número indicado en una cadena de texto 
        con formato moneda.
        """
        return "{}{:,}".format(simbolo, round(numero, 2))

    def Strip(self, texto):
        """
        Elimina los espacios extras del texto indicado.
        """
        return texto.replace("     ", " ").replace("    ", " ").replace("   ", " ").replace("  ", " ").strip()

    def Int(self, texto, intext=False):
        """
        Obtiene un número entero a partir del texto introduccido, eliminando 
        los caracteres que no sean númericos. Si hay un punto, los caracteres a 
        la derecha del punto serán omitidos.
        Si 'intext' es True, retorna el número como un objeto string.
        """
        n = ""
        for c in texto:
            if c == ".":
                break
            elif c in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9"):
                n += c
        if intext:
            return str(int(n))
        return int(n)

    def Float(self, texto, intext=False):
        """
        Obtiene un número de coma flotante a partir del texto introduccido,
        eliminando los caracteres que no sean numéricos, exceptuando el punto.
        Si 'intext' es True, retorna el número como un objeto string.
        """
        n = ""
        for c in texto:
            if c in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."):
                n += c
        if intext:
            return str(float(n))
        return float(n)

    def Decimal(self, texto, intext=False):
        """
        Obtiene un número Decimal a partir del texto introduccido, 
        eliminado los carácteres que no sean numéricos, exceptuando el punto.
        Si 'intext' es True, retorna el número como un objeto string.
        """
        if not texto:
            return Decimal()
        floatObj = self.Float(texto, intext)
        if intext:
            return floatObj
        return Decimal(str(floatObj))

    def ValidarCedula(self, texto, div="-"):
        """
        Valida que el formato de texto introducido corresponda 
        a un formato de documento de identidad nacional válido para la Rep. Dom., 
        y retorna la cédula en su formato correspondiente.
        return: str
        """
        texto = texto.replace(" ", "").replace("-", "")
        for c in texto:
            if not c in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9"):
                raise ValueError(_("La cédula contiene caracteres no válidos."))
            elif len(texto) != 11:
                raise ValueError(_("La cédula debe contener exactamente 11 dígitos."))
        return "{a}{div}{b}{div}{c}".format(a=texto[:3], b=texto[3:10], c=texto[10], div=div)

    def ValidarNombre(self, texto):
        """
        Valida que el texto introduccido pueda ser utilizado como 
        un nombre válido para una persona.
        """
        out = self.Strip(texto).title()
        if not self.IsPossibleName(out):
            raise ValueError(_("El texto indicado no parece ser el nombre válido de una persona."))
        return out

    def IsCedulaValida(self, texto):
        try:
            self.ValidarCedula(texto)
        except BaseException:
            return False
        return True
            





class Numero(object):
    """
    Clase para trabajar con números.
    """

    def MontoText(self, monto, moneda="", html=False):
        if not isinstance(moneda, str):
            moneda = ""
        if html == True:
            if monto < 0:
                return '<span style="color: red">{:,.2f} {}</span>'.format(monto, moneda)
            return '<span>{:,.2f} {}</span>'.format(monto, moneda)
        return "{:,.2f} {}".format(monto, moneda)

    def MontoHtml(self, monto, moneda=""):
        return self.MontoText(monto, moneda, True)





class Fecha(object):
    """
    Clase para el manejo de fechas.
    """

    def CompararFechas(self, fecha1, fecha2, operator="=="):
        """
        Realiza la operación de comparación de las dos fechas indicadas de 
        acuerdo al operador de comparación indicado.
        """
        try:
            fecha1.year 
            fecha2.year 
        except AttributeError as e:
            raise ValueError("Las fechas indicadas deben ser objetos de fechas válida en python.")
        # Si una o ambas fechas es un objeto datetime.date no (datetime.datetime)
        # la otra fecha se pasará a date.
        if (isinstance(fecha1, datetime.date) or (isinstance(fecha2, datetime.date))):
            fecha1 = datetime.date(fecha1.year, fecha1.month, fecha1.day)
            fecha2 = datetime.date(fecha2.year, fecha2.month, fecha2.day)
        try:
            fecha1.hours
            fecha2.hours
        except AttributeError as e:
            fecha1 = datetime.date(fecha1.year, fecha1.month, fecha1.day)
            fecha2 = datetime.date(fecha2.year, fecha2.month, fecha2.day)
        
        if operator in ("==", "="):
            return fecha1 == fecha2 
        if operator == "<":
            return fecha1 < fecha2 
        if operator in ("<=", "=<"):
            return fecha1 <= fecha2
        if operator == ">":
            return fecha1 > fecha2 
        if operator in (">=", "=>"):
            return fecha1 >= fecha2 
        if operator in ("!=", "=!", "not"):
            return fecha1 != fecha2
        
        raise ValueError("El operador '{}' no es válido.".format(operator))

    def GetTiempo(self, fecha1, fecha2=datetime.date.today(), intexto=False):
        """
        Obtiene la diferencia (tiempo) entre dos fechas.
        """
        try:
            timedelta = fecha2 - fecha1
            days = timedelta.days
            years = int(days / 365)
        except TypeError:
            days = 0
            years = 0
        if intexto == True:
            if years > 0:
                return "{} años".format(years)
            return "{} dias".format(days)
        return days

    def GetEdad(self, fecha, intexto=False):
        """
        Calcula la edad correspondiente a la fecha indicada.
        """
        return self.GetTiempo(fecha1=fecha, intexto=intexto)

    def GetListadoDeFechas(self, inicio=datetime.date.today(), periodo=MENSUAL, limite=None, fin=None):
        """
        Obtiene un listado con las fechas en el rango dado.

        inicio = fecha de inicio.
        periodo = 'diario' | 'interdiario' | 'semanal' | 'quincenal' | 'mensual' | 'anual' 
        limite = cantidad de fechas en el listado.
        fin = fecha límite (opcional).

        Nota: Entre 'limite' y 'fin' se usará el que primero se cumpla. Asi que si se desea 
        asegurar que la fecha última sea hasta el 'fin', deberá establecer un limite alto (casi inalcanzable)
        para que le de tiempo a la condición 'fin' cumplirse.
        """
        inicio = datetime.date(inicio.year, inicio.month, inicio.day)
        if not limite:
            limite = 1000000000
        if fin:
            fin = datetime.date(fin.year, fin.month, fin.day)
        periodo = periodo.upper()
        fechas = [inicio]
        fecha = inicio

        if periodo == DIARIO:
            year, month, day = fecha.year, fecha.month, fecha.day
            for i in range(limite):
                fecha = fecha + datetime.timedelta(days=1)
                fechas.append(fecha)
                if (fin):
                    if (fecha >= fin):
                        break
            return fechas

        if periodo == QUINCENAL:
            year, month = fecha.year, fecha.month
            for i in range(limite):
                fecha = fecha + datetime.timedelta(days=15)
                fechas.append(fecha)
                if (fin):
                    if (fecha >= fin):
                        break 
            return fechas 
                
        if periodo == MENSUAL:
            year, month = fecha.year, fecha.month
            for i in range(limite):
                # Se suman los meses, si el mes es el último, entonces se suma un año
                # y se reinicia el mes a 1 nuevamente.
                day = inicio.day
                if month == 12:
                    month = 1
                    year += 1
                else:
                    month += 1
                # Si el día es más alto al maximo del mes, entonces se considera
                # como día el último día del mes.
                for n in range(10):
                    try:
                        fecha = datetime.date(year, month, day)
                    except ValueError:
                        day -= 1
                    else:
                        break 
                if (fin) and (fecha > fin):
                    break
                fechas.append(fecha)
            return fechas

    def GetRangoDeFechas(self, inicio, fin=datetime.date.today(), periodo=MENSUAL):
        """
        Obtiene un listado de todas las fechas comprendidas 
        en el rango de fechas indicado.
        """
        return self.GetListadoDeFechas(inicio, periodo, 999999999999, fin)

    def GetUltimoDiaDelMes(self, year=None, month=None):
        """
        Obtiene el ultimo dia del mes indicado. Si no se indica mes 
        se tomará como referencia la fecha actual.
        """
        if not year:
            year = datetime.date.today().year 
        if not month:
            month = datetime.date.today().month 
        day = 31
        for n in range(10):
            try:
                fecha = datetime.date(year, month, day)
            except ValueError:
                day -= 1
            else:
                break
        return fecha 



class Encriptado(encriptado.Encriptado):
	"""
    Clase para encriptar texto. 
    """






class PrestamoBase(Fecha):
    """
    Clase para las operaciones de cálculo de un préstamo.
    """

    def GetDuraccion(self, fecha_inicio, cant_cuotas, periodo=MENSUAL):
        """
        Obtiene el tiempo de duración del préstamo, desde la fecha
        de inicio (desembolso) hasta la fecha en que concluirá según 
        la cantidad de cuotas y el periodo en que se generan dichas cuotas.
        
        ---> (int(years), int(months), int(days))
        """

    def GetAmortizacionCuotaFija(self, monto, tasa, cuotas, periodo=MENSUAL, inicio=datetime.date.today()):
        """
        Args:
            monto (float): monto del préstamo.
            tasa (float): tasa del préstamo.
            cuotas (int): cantidad de cuotas.
            periodo (str): periodo del préstamo (semanal, quincenal, mensual, ...).
            inicio (datetime.date): fecha de inicio del préstamo.

        Returns:
            list: Una lista de dicionarios.
        """
        # Calculamos el valor de la cuota.
        valor, interes, capital_restante = self.GetValorDeCuotaFija(monto, tasa, cuotas, periodo)
        # Obtenemos el listado de cortes.
        fechas = self.GetListadoDeFechas(inicio, periodo, cuotas)
        tabla = []
        # Variables para los totales.
        t_valor, t_interes, t_capital, t_capital_restante = Decimal(), Decimal(), Decimal(), Decimal()
        
        n = 1 # Número de cuota.
        for fecha in fechas[1:]:
            # Calculamos el interés generado en este corte.
            interes = capital_restante * (tasa / Decimal(100))
            # Calculamos el capital restante.
            capital = valor - interes
            capital_restante -= capital
            # Agregamos el corte al listado.
            tabla.append({
                "cuota": n,
                "fecha": fecha,
                "valor": round(valor, 2),
                "interes": round(interes, 2),
                "capital": round(capital, 2),
                "capital_restante": round(capital_restante, 2),
                "clase": "item",
            })
            # Sumamos el corte a los totales.
            t_valor += valor 
            t_interes += interes
            t_capital += capital
            t_capital_restante = capital_restante
            n += 1
        # Agregamos los totales en el último item del listado.
        tabla.append({
            "cuota": "",
            "fecha": "Total",
            "valor": round(t_valor, 2),
            "interes": round(t_interes, 2),
            "capital": round(t_capital, 2),
            "capital_restante": round(t_capital_restante, 2),
            "clase": "total",
        })
        return tabla

    def GetAmortizacionCuotaVariable(self, monto, tasa, cuotas, periodo=MENSUAL, inicio=datetime.date.today()):
        """
        Retorna un listado de diccionarios que contienen 
        información de las cuotas de la tabla de amortización 
        de un préstamo con cuota de tipo variable.
        """
        capital_restante = monto
        cuotas = cuotas 
        tasa = tasa
        periodo = periodo   
        fechas = self.GetListadoDeFechas(inicio, periodo, cuotas)
        tabla = []
        capital = capital_restante / cuotas
        t_valor, t_interes, t_capital, t_capital_restante = Decimal(), Decimal(), Decimal(), Decimal()
        
        n = 1 # Número de cuota.
        for fecha in fechas[1:]:
            interes = (capital_restante / Decimal(100)) * tasa
            valor = capital + interes 
            capital_restante = capital_restante - capital

            tabla.append({
                "cuota": n,
                "fecha": fecha,
                "valor": round(valor, 2),
                "interes": round(interes, 2),
                "capital": round(capital, 2),
                "capital_restante": round(capital_restante, 2),
                "clase": "item",
            })
            t_valor += valor 
            t_interes += interes
            t_capital += capital
            t_capital_restante = capital_restante
            n += 1
        # Agregamos los totales en el último item.
        tabla.append({
            "cuota": "",
            "fecha": "Total",
            "valor": round(t_valor, 2),
            "interes": round(t_interes, 2),
            "capital": round(t_capital, 2),
            "capital_restante": round(t_capital_restante, 2),
            "clase": "total",
        })
        return tabla

    def GetAmortizacionTitulos(self):
        """
        Obtiene los nombres de las columnas de la tabla de amortización.
        """
        return (_("Cuota"), _("Fecha"), _("Valor"), _("Interés"), _("Capital"), _("Capital restante"))

    def GetComportamientoDePagosCuotaFija(self, monto, tasa, cuotas, interesmora, periodo=MENSUAL, inicio=datetime.date.today(), pagos=[]):
        """
        Obtiene el comportamiento de pagos de un préstamo.
        Los pagos deben ser un listado de tuplas (fecha, montopagado).
        """
        pagos = [[fecha, monto, False] for fecha, monto in pagos]
        comp = []
        # Obtenemos el valor de la cuota del préstamo.
        valor, interes, capital = self.GetValorDeCuotaFija(monto, tasa, cuotas, periodo, limit_dec=2)
        capital_restante = capital
        # La diferencia es el remanente que queda despues de haber pagado de menos o de más,
        # lo cual se va a sumar o restar en el próximo corte según sea el caso.
        diferencia = 0 
        # La mora es el valor adicional que se le sumará al monto por pagar en caso de atrasos en el pago.
        mora = 0 
        # Indica si la cuota está o no vencida por pago pendiente cuando la fecha de pago pasó.
        vencida = False
        # Obtenemos las fechas en que se generarán las cuotas.
        cortes = self.GetListadoDeFechas(inicio, periodo, limite=cuotas)
        n = 1 # Número de la cuota.
        for corte in cortes[1:]:
            # Obtenemos la sumatoria de todos los pagos realizados en la fecha de corte correspondiente.
            # Asegurandonos de poner istomado en True para evitar que sea tomado en cortes posteriores.
            pagado = 0
            i = 0
            for fecha, pago, istomado in pagos.copy():
                if istomado == False:
                    if fecha <= corte:
                        pagado += pago
                        pagos[i][2] = True 
                i += 1 
            # Monto a pagar generado en este corte, el cual es igual a la sumatoria del 
            # valor de la cuota, más el monto remanente del corte anterior, más el monto por mora si lo hay.
            # el balance a pagar no se reduce por los pagos, este balance queda como prueba que fue el monto
            # que se generó a pagar en este corte, diferente del 'por pagar' que si se reduce con los pagos.
            apagar = valor + diferencia + mora
            # El saldo anterior a favor o en contra, es extraido de la diferencia calculada en el corte anterior.
            saldo_anterior = diferencia
            # La mora cargada en este corte, es extraida del cálculo que se hizo de la mora en el corte anterior.
            mora_cargada = mora 

            # Si la fecha de corte pasó:
            if corte < datetime.date.today():
                # Si se realizó el pago completo a lo justo.
                if pagado == apagar:
                    mora = 0
                    vencida = False
                # Si no se realizó pago o no se pago completo.
                # generamos una mora, la cual es equivalente a un porcentaje del valor
                # de la cuota (valor de la cuota sin interés ni otros cargos.)
                elif pagado < apagar:
                    mora = round((valor / 100) * interesmora, 2)
                    vencida = True
                # Si el monto pagado fue mayor a lo que debió pagarse.
                elif pagado > apagar:
                    mora = 0
                    vencida = False
            # Si aún no vence la fecha de pago. Esta fecha aun no ha llegado, por lo cual no 
            # es necesario que se pague, asi que no generamos mora ni 
            else:
                mora = 0
                vencida = False


            diferencia = apagar - pagado
            # Por pagar es el balance que el cliente tiene pendiente pagar. Este balance es 
            # el balance generado a pagar en el corte, restándole el monto que ya se ha pagado.
            # Si por pagar es menor que 0, se establece por pagar igual a 0.
            porpagar = apagar - pagado 
            if porpagar < 0:
                porpagar = 0
            
            interes = round((capital_restante + saldo_anterior) * (tasa / Decimal(100)), 2)
            capital = apagar - interes 
            capital_restante -= capital 

            # Agregamos el comportamiento de este corte.
            comp.append({
                "corte": corte, # fecha de corte.
                "apagar": apagar, # monto cargado que se deberá pagar.
                "pagado": pagado, # monto que se ha pagado ya en este corte.
                "porpagar": porpagar, # monto por pagar restante en caso de ya haber pagos.
                "mora": mora_cargada, # comisión por mora cargada en caso de atrasos
                "diferencia": diferencia, # Diferencia reflejada entre el valor absoluto de la cuota y el monto a pagar.
                "saldo_anterior": saldo_anterior, # Saldo a favor o en contra que queda del anterior corte.
                "valor": valor, # Valor absoluto de la cuota.
                "interes": interes,
                "capital": capital,
                "capital_restante": capital_restante,
                "cuota": n, # Número de la cuota.
                "vencida": vencida, # Indica si está cuota está o no vencida (bool).
                "clase": {True: "cuotavencida", False: "cuotanormal", None: ""}[vencida], # Clase para usar en style CSS.
            })

            n += 1

        # Una vez que se han cumplido todas las cuotas, pero aún queda 
        # saldo pendiente por pagar, se generarán cuotas (solo con el valor adeudado) por 
        # cada corte extra cumplido hasta la fecha actual, y su respectiva mora cargada.

        # Obtenemos el último corte del comportamiento, y verificamos que este tenga 
        # aún un balance pendiente por pagar.
        last = comp[-1]
        if last["porpagar"] > 0:
            # Generamos los corte desde la fecha del último corte, hasta el día de hoy.
            cortes = self.GetListadoDeFechas(last["corte"], periodo, fin=datetime.date.today())
            # Obtenemos algunas informaciones del último corte.
            apagar = last["apagar"]
            diferencia = last["diferencia"]
            mora = last["mora"]
            # El número de cuota continua donde quedó el último corte.
            n = cuotas + 1
            for corte in cortes[1:]:
                # Obtenemos la suma de los pagos que se realizaron en este corte.
                pagado = 0
                i = 0
                for fecha, pago, istomado in pagos.copy():
                    if istomado == True:
                        continue 
                    elif fecha <= corte:
                        pagado += pago
                        pagos[i][2] = True 
                    i += 1 
                # No se generan más cuotas, sino que se le suma la mora al monto vencido.
                apagar += mora
                mora_cargada = mora 
                # Se realiza la comprobación para verificar si se ha pagado el corte
                # completo o parcial, o nada, para determinar si se seguirá generando moras.
                if pagado == apagar:
                    mora = 0
                    vencida = False
                elif pagado < apagar:
                    mora = round((valor / 100) * interesmora, 2)
                    vencida = True
                elif pagado > apagar:
                    mora = 0
                    vencida = False
                # Obtenemos el monto por pagar:
                diferencia = apagar - pagado
                porpagar = apagar - pagado 
                if porpagar < 0:
                    porpagar = 0

                interes = round((capital_restante + saldo_anterior) * (tasa / Decimal(100)), 2)
                capital = apagar - interes 
                capital_restante -= capital 

                # Agregamos la nueva cuota al comportamiento.
                comp.append({
                    "corte": corte, # fecha de corte.
                    "apagar": apagar, # monto cargado que se deberá pagar.
                    "pagado": pagado, # monto que se ha pagado ya en este corte.
                    "porpagar": porpagar, # monto por pagar restante en caso de ya haber pagos.
                    "mora": mora_cargada, # comisión por mora cargada en caso de atrasos
                    "diferencia": diferencia, # Diferencia reflejada entre el valor absoluto de la cuota y el monto a pagar.
                    "saldo_anterior": saldo_anterior, # Saldo a favor o en contra que queda del anterior corte.
                    "valor": valor, # Valor absoluto de la cuota.
                    "interes": interes,
                    "capital": capital,
                    "capital_restante": capital_restante,
                    "cuota": n, # Número de la cuota.
                    "vencida": vencida, # Indica si está cuota está o no vencida (bool).
                    "clase": "cuotavencidaextra", # Clase para usar en style CSS.
                })
                n += 1

        # Estadisticas.
        stat = {}
        stat["cuotas_vencidas"] = len([c for c in comp if c["vencida"]]) # Cantidad de cuotas vencidas.
        # Retornamos los datos en un diccionario.
        return {"comportamiento": comp, "estadisticas": stat}

    def GetProximoPago(self, monto, tasa, cuotas, interesmora, periodo=MENSUAL, inicio=datetime.date.today(), pagos=[]):
        """
        Obtiene la información del próximo pago que deberá realizarce.
        """
        comportamiento = self.GetComportamientoDePagosCuotaFija(monto, tasa, cuotas, interesmora, periodo, inicio, pagos)["comportamiento"]
        for comp in comportamiento:
            # Verificamos la cuota más próxima que aun no se ha pagado en su totalidad.
            if (comp["corte"] >= datetime.date.today()):
                if (comp["pagado"] < comp["apagar"]):
                    return comp 

        # Si ya todas las cuotas se han cumplido,
        # pero aun queda balance pendiente.
        comp = comportamiento[-1]
        if comp["porpagar"] > 0:
            return comp
        
    def GetValorDeCuotaFija(self, monto, tasa, cuotas, periodo=MENSUAL, limit_dec=None):
        """
        Retorna el valor actual de la cuota, según el método francés,
        en donde las cuotas son fijas. -> float(x)

        Formula = R = P [(i (1 + i)**n) / ((1 + i)**n – 1)].
        Donde:
            R = renta (cuota)
            P = principal (préstamo adquirido)
            i = tasa de interés
            n = número de periodos
            
        -> (Moneda valor, Moneda interes, Moneda monto)
        """
        tasa = tasa / Decimal(100)
        if periodo == DIARIO:
            tasa /= Decimal(30.4167)
        elif periodo == SEMANAL:
            tasa /= Decimal(4.34524)
        if periodo == QUINCENAL:
            tasa /= Decimal(2.0)
        elif periodo == ANUAL:
            tasa *= 12

        # Si no se especifica una tasa, se pone un número casi imperceptible para 
        # evitar que la formula lanze una excepción de división por cero.
        if not tasa:
            tasa = Decimal(0.00000000001)
        # Furmula para el cálculo según el sistema francés.
        valor = monto * ( (tasa * ((1 + tasa)**cuotas)) / (((1 + tasa)**cuotas) - 1) )
        interes = valor - monto
        if limit_dec:
            return (round(valor, limit_dec), round(interes, limit_dec), round(monto, limit_dec))
        return (valor, interes, monto)

    def GetValorDeCuotaVariable(self, capital, tasa, periodo=MENSUAL):
        """
        Retorna una tupla con el valor de la cuota, el interes y el capital.
        para prestamos con cuotas variables.
        --> (valor, interes, capital)
        """
        interes = (capital / 100) * tasa
        if periodo == DIARIO:
            interes /= 30.4167
        elif periodo == SEMANAL:
            interes /= 4.34524
        if periodo == QUINCENAL:
            interes /= 2.0
        elif periodo == ANUAL:
            interes *= 12

        valor = capital + interes
        return (valor, interes, capital)










