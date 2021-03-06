from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader
import json as simplejson
from .models import Cheque, Empresa, Historico
import datetime
import locale
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as django_logout
from xhtml2pdf import pisa
from django.views import View
from io import BytesIO
from django.template.loader import get_template
from django.db.models import Sum
from django.conf import settings
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

locale.setlocale(locale.LC_ALL, "")
ULTIMA_EMPRESA = None

def render_to_pdf(template_src, context_dict=None):
	if context_dict is None:
		context_dict = {}
	template = get_template(template_src)
	html  = template.render(context_dict)
	result = BytesIO()
	pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
	if not pdf.err:
		return HttpResponse(result.getvalue(), content_type='application/pdf')
	return None

#Automaticly downloads to PDF file
class DownloadPDF(View):
    def get(self, request, *args, **kwargs):
        query = {
            "dt_liberacao_ini": request.GET.get("dt_liberacao_ini"),
            "dt_liberacao_fim": request.GET.get("dt_liberacao_fim"),
            "dt_cadastro_ini": request.GET.get("dt_cadastro_ini"),
            "dt_cadastro_fim": request.GET.get("dt_cadastro_fim"),
            "empresa": request.GET.get("empresa"),
            "destinatario": request.GET.get("destinatario"),
            "ordem_dt_cadastro": request.GET.get("ordem_dt_cadastro"),
            "ordem_dt_liberacao": request.GET.get("ordem_dt_liberacao"),
            "user": request.user
        }

        filters = Q(user=request.user)
        filtros = {}
        lista_filtros=[]
        if query["empresa"] != "0":
            filters &= Q(empresa_id=query["empresa"])
            filtros["empresa"] = query["empresa"]
            lista_filtros.append(query["empresa"])
        if query["destinatario"]:
            filters &= Q(destinatario__icontains=query["destinatario"])
            filtros["destinatario"] = query["destinatario"]
            lista_filtros.append(query["destinatario"])
        if query["dt_cadastro_ini"]:
            filters &= Q(dt_record__gte=query["dt_cadastro_ini"])
            filtros["dt_cadastro_ini"] = query["dt_cadastro_ini"]
            lista_filtros.append(query["dt_cadastro_ini"])
        if query["dt_cadastro_fim"]:
            filters &= Q(dt_record__lte=query["dt_cadastro_fim"])
            filtros["dt_cadastro_fim"] = query["dt_cadastro_fim"]
            lista_filtros.append(query["dt_cadastro_fim"])
        if query["dt_liberacao_ini"]:
            filters &= Q(dt_futura__gte=query["dt_liberacao_ini"])
            filtros["dt_liberacao_ini"] = query["dt_liberacao_ini"]
            lista_filtros.append(query["dt_liberacao_ini"])
        if query["dt_liberacao_fim"]:
            filters &= Q(dt_futura__lte=query["dt_liberacao_fim"])
            filtros["dt_liberacao_fim"] = query["dt_liberacao_fim"]
            lista_filtros.append(query["dt_liberacao_fim"])

        lista_cheques = Cheque.objects.filter(filters).order_by("dt_futura")

        context = {"lista_cheques": lista_cheques,
                   "valor_total": lista_cheques.aggregate(Sum('valor'))['valor__sum']}

        if lista_filtros:
            context = {"lista_cheques": lista_cheques,
                    "lista_filtros": lista_filtros,
                    "valor_total": lista_cheques.aggregate(Sum('valor'))['valor__sum']}

        pdf = render_to_pdf('cheques/pdf_template.html', context)
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"relatorio{datetime.datetime.today().strftime('%d-%m-%Y-%H:%M:%S')}.pdf"
        content = "attachment; filename=%s" % (filename)
        response['Content-Disposition'] = content
        return response

def home(request):
    return redirect("index")

def logout(request):
    django_logout(request)
    return redirect("index")

@login_required
def mantem_filtros(request):
    if request.method == "GET":
        user = request.user.id
        lista_empresas = Empresa.objects.filter(user=user)
        lista_cheques = Cheque.objects.filter(user=user).order_by("dt_futura")
        print(request.get_full_path())
        query = {
            "dt_liberacao_ini": request.GET.get("dt_liberacao_ini"),
            "dt_liberacao_fim": request.GET.get("dt_liberacao_fim"),
            "dt_cadastro_ini": request.GET.get("dt_cadastro_ini"),
            "dt_cadastro_fim": request.GET.get("dt_cadastro_fim"),
            "empresa": request.GET.get("empresa"),
            "destinatario": request.GET.get("destinatario"),
            "nr_cheque": request.GET.get("nr_cheque"),
            "qtd_itens_pag": request.GET.get("qtd_itens_pag")
        }

        print(query)

        data = simplejson.dumps(query)
        return HttpResponse(data, content_type="application/json")

@login_required
def index(request):
    user = request.user.id
    lista_empresas = Empresa.objects.filter(user=user)

    query = {
        "dt_liberacao_ini": request.GET.get("dt_liberacao_ini"),
        "dt_liberacao_fim": request.GET.get("dt_liberacao_fim"),
        "dt_cadastro_ini": request.GET.get("dt_cadastro_ini"),
        "dt_cadastro_fim": request.GET.get("dt_cadastro_fim"),
        "empresa": request.GET.get("empresa"),
        "destinatario": request.GET.get("destinatario"),
        "ordem_dt_cadastro": request.GET.get("ordem_dt_cadastro"),
        "ordem_dt_liberacao": request.GET.get("ordem_dt_liberacao"),
        "nr_cheque": request.GET.get("nr_cheque"),
        "user": request.user.id,
        "qtd_itens_pag": request.GET.get("qtd_itens_pag")
    }
    qtd_itens_pag = query["qtd_itens_pag"]
    filters = Q(user=user)
    filtros = {}
    if query["empresa"] != "0":
        filters &= Q(empresa_id=query["empresa"])
        filtros["empresa"]=query["empresa"]
    if query["destinatario"]:
        filters &= Q(destinatario__icontains=query["destinatario"])
        filtros["destinatario"] = query["destinatario"]
    if query["dt_cadastro_ini"]:
        filters &= Q(dt_record__gte=query["dt_cadastro_ini"])
        filtros["dt_cadastro_ini"] = query["dt_cadastro_ini"]
    if query["dt_cadastro_fim"]:
        filters &= Q(dt_record__lte=query["dt_cadastro_fim"])
        filtros["dt_cadastro_fim"] = query["dt_cadastro_fim"]
    if query["dt_liberacao_ini"]:
        filters &= Q(dt_futura__gte=query["dt_liberacao_ini"])
        filtros["dt_liberacao_ini"] = query["dt_liberacao_ini"]
    if query["dt_liberacao_fim"]:
        filters &= Q(dt_futura__lte=query["dt_liberacao_fim"])
        filtros["dt_liberacao_fim"] = query["dt_liberacao_fim"]
    if query["nr_cheque"]:
        filters &= Q(nr_cheque=query["nr_cheque"])
        filtros["nr_cheque"] = query["nr_cheque"]
    if query["qtd_itens_pag"]:
        filtros["qtd_itens_pag"] = query["qtd_itens_pag"]

    lista_cheques = Cheque.objects.filter(filters).order_by("dt_futura")
    
    query.pop("user")
    if all(value == None for value in query.values()) :
        lista_cheques = Cheque.objects.filter(user=user).order_by("dt_futura")

    page = request.GET.get('page', 1)

    nr_pages = query["qtd_itens_pag"]
    if query["qtd_itens_pag"] == None:
        nr_pages = query["qtd_itens_pag"] = 50

    paginator = Paginator(lista_cheques, nr_pages)
    try:
        lista_cheques = paginator.page(page)
    except PageNotAnInteger:
        lista_cheques = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    print(filtros)
    context = {"lista_cheques": lista_cheques, "lista_empresas": lista_empresas, "filtros": filtros}
    return render(request, "cheques/index.html", context)

@login_required
def add(request):
    if request.method == "GET":
        return HttpResponse("get")
    if request.method == "POST":
        itens = {
            "nr_cheque": request.POST.get("nr_cheque"),
            "valor": request.POST.get("valor"),
            "empresa": Empresa.objects.get(pk=request.POST.get("empresa")),
            "banco": request.POST.get("banco"),
            "agencia": request.POST.get("agencia"),
            "conta": request.POST.get("conta"),
            "dt_futura": request.POST.get("dt_futura"),
            "dt_record": datetime.datetime.today(),
            "destinatario": request.POST.get("destinatario"),
            "user": request.user
        }

        cheque_instance = Cheque.objects.create(**itens)
        ULTIMA_EMPRESA = Empresa.objects.get(pk=request.POST.get("empresa"))
        return redirect("index")

@login_required
def novo(request):
    user = request.user.id
    lista_cheques = Cheque.objects.filter(user=user)
    lista_empresas = Empresa.objects.filter(user=user)
    context = {"lista_cheques": lista_cheques, "lista_empresas": lista_empresas, "ultima_empresa": ULTIMA_EMPRESA}
    return render(request, "cheques/novo.html", context)

@login_required
def get_data(request, id):
    if request.method == "GET":
        obj = Empresa.objects.get(id=id)
        data_dict = {"conta": obj.conta, "banco": obj.banco, "agencia": obj.agencia}
        data = simplejson.dumps(data_dict)
        return HttpResponse(data, content_type="application/json")



@login_required
def cadastro(request):
    user = request.user.id
    lista_cheques = Cheque.objects.filter(user=user)
    lista_empresas = Empresa.objects.filter(user=user).order_by("nome")
    context = {
        "lista_cheques": lista_cheques,
        "lista_empresas": lista_empresas,
    }
    return render(request, "cheques/cadastro.html", context)


@login_required
def hist(request):
    user = request.user.id
    lista_cheques = Cheque.objects.filter(user=user)
    lista_empresas = Empresa.objects.filter(user=user)
    lista_historico = Historico.objects.filter(user=user).order_by("dt_comp_excl")
    context = {
        "lista_cheques": lista_cheques,
        "lista_empresas": lista_empresas,
        "lista_historico": lista_historico,
    }
    return render(request, "cheques/hist.html", context)


@login_required
def addcadastro(request):
    user = request.user.id
    if request.method == "GET":
        return HttpResponse("get")
    if request.method == "POST":
        itens = {
            "nome": request.POST.get("nome"),
            "cpfpj": request.POST.get("cpfpj"),
            "banco": request.POST.get("banco"),
            "agencia": request.POST.get("agencia"),
            "conta": request.POST.get("conta"),
            "dt_record": datetime.datetime.today(),
            "user": request.user
        }
        empresa_instance = Empresa.objects.create(**itens)
        return redirect("cadastro")


@login_required
def chequesdel(request, id=None):
    if request.method == "GET":
        instance = Cheque.objects.get(id=id)
        hist = {
            "nr_cheque": instance.nr_cheque,
            "valor": instance.valor,
            "empresa": instance.empresa,
            "banco": instance.banco,
            "agencia": instance.agencia,
            "conta": instance.conta,
            "dt_futura": instance.dt_futura,
            "dt_record": datetime.datetime.today(),
            "destinatario": instance.destinatario,
            "dt_comp_excl": datetime.datetime.now(),
            "compensado": False,
            "user": request.user
        }
        historico_instance = Historico.objects.create(**hist)
        historico_instance.save()
        instance.delete()
        return redirect("index")


@login_required
def compensar(request, id=None):
    if request.method == "GET":
        instance = Cheque.objects.get(id=id)
        hist = {
            "nr_cheque": instance.nr_cheque,
            "valor": instance.valor,
            "empresa": instance.empresa,
            "banco": instance.banco,
            "agencia": instance.agencia,
            "conta": instance.conta,
            "dt_futura": instance.dt_futura,
            "dt_record": datetime.datetime.today(),
            "destinatario": instance.destinatario,
            "dt_comp_excl": datetime.datetime.now(),
            "compensado": True,
            "user": request.user
        }
        historico_instance = Historico.objects.create(**hist)
        historico_instance.save()
        instance.delete()
        return redirect("index")


@login_required
def editar(request, id=None):
    if request.method == "GET":
        user = request.user.id
        lista_cheques = Cheque.objects.filter(user=user)
        lista_empresas = Empresa.objects.filter(user=user)
        edit = Cheque.objects.get(id=id)
        context = {
            "lista_cheques": lista_cheques,
            "lista_empresas": lista_empresas,
            "agencia": edit.agencia,
            "dt_futura": edit.dt_futura,
            "empresa": edit.empresa,
            "banco": edit.banco,
            "valor": str(edit.valor).replace(",", "."),
            "conta": edit.conta,
            "destinatario": edit.destinatario,
            "nr_cheque": edit.nr_cheque,
            "id": id,
        }
        return render(request, "cheques/editar.html", context)
    return redirect("editar")


@login_required
def edit(request):
    if request.method == "GET":
        return HttpResponse("get")
    if request.method == "POST":
        id = request.POST.get("id")
        cheque_instance = Cheque.objects.get(id=id)
        cheque_instance.nr_cheque= request.POST.get("nr_cheque")
        cheque_instance.valor= request.POST.get("valor")
        cheque_instance.agencia= request.POST.get("agencia")
        cheque_instance.conta= request.POST.get("conta")
        cheque_instance.banco= request.POST.get("banco")
        cheque_instance.empresa= Empresa.objects.get(pk=request.POST.get("empresa"))
        cheque_instance.dt_futura= request.POST.get("dt_futura")
        cheque_instance.destinatario= request.POST.get("destinatario")
        
        cheque_instance.save()
        return redirect("index")

@login_required
def cadastrodel(request, id=None):
    if request.method == "GET":
        instance = Empresa.objects.get(id=id)
        instance.delete()
        return redirect("cadastro")


@login_required
def limparhist(request, id=None):
    if request.method == "GET":
        instance = Historico.objects.all().delete()
        return redirect("hist")
