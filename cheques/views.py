from django import http
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader
import json as simplejson
from .models import Cheque, Empresa, Historico
import datetime
import locale
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as django_logout

locale.setlocale(locale.LC_ALL, "")
ULTIMA_EMPRESA = None

def home(request):
    return redirect("index")


def logout(request):
    django_logout(request)
    return redirect("index")


@login_required
def index(request):
    lista_empresas = Empresa.objects.all()
    lista_cheques = Cheque.objects.all()

    query = {
        "dt_liberacao_ini": request.GET.get("dt_liberacao_ini"),
        "dt_liberacao_fim": request.GET.get("dt_liberacao_fim"),
        "dt_cadastro_ini": request.GET.get("dt_cadastro_ini"),
        "dt_cadastro_fim": request.GET.get("dt_cadastro_fim"),
        "empresa": request.GET.get("empresa"),
        "banco": request.GET.get("banco"),
        "ordem_dt_cadastro": request.GET.get("ordem_dt_cadastro"),
        "ordem_dt_liberacao": request.GET.get("ordem_dt_liberacao"),
    }

    if query["dt_liberacao_ini"] and query["dt_liberacao_fim"]:
        lista_cheques = Cheque.objects.filter(
            dt_futura__gte=query["dt_liberacao_ini"],
            dt_futura__lte=query["dt_liberacao_fim"],
        )
    elif query["dt_liberacao_ini"] and not query["dt_liberacao_fim"]:
        lista_cheques = Cheque.objects.filter(dt_futura__gte=query["dt_liberacao_ini"])
    elif query["dt_liberacao_fim"] and not query["dt_liberacao_ini"]:
        lista_cheques = Cheque.objects.filter(dt_futura__lte=query["dt_liberacao_fim"])

    if query["dt_cadastro_ini"] and query["dt_cadastro_fim"]:
        lista_cheques = Cheque.objects.filter(
            dt_futura__gte=query["dt_cadastro_ini"],
            dt_futura__lte=query["dt_cadastro_fim"],
        )
    elif query["dt_cadastro_ini"] and not query["dt_cadastro_fim"]:
        lista_cheques = Cheque.objects.filter(dt_futura__gte=query["dt_cadastro_ini"])
    elif query["dt_cadastro_fim"] and not query["dt_cadastro_ini"]:
        lista_cheques = Cheque.objects.filter(dt_futura__lte=query["dt_cadastro_fim"])

    if query["empresa"] and query["empresa"] != "0":
        lista_cheques = Cheque.objects.filter(empresa_id=int(query["empresa"]))

    if query["banco"] and query["banco"] != "0":
        lista_cheques = Cheque.objects.filter(banco_id=int(query["banco"]))

    if query["ordem_dt_cadastro"]:
        lista_cheques = Cheque.objects.order_by("dt_record")
    if query["ordem_dt_liberacao"]:
        lista_cheques = Cheque.objects.order_by("dt_futura")

    context = {"lista_cheques": lista_cheques, "lista_empresas": lista_empresas}
    return render(request, "cheques/index.html", context)


@login_required
def novo(request):
    lista_cheques = Cheque.objects.all()
    lista_empresas = Empresa.objects.all()
    context = {"lista_cheques": lista_cheques, "lista_empresas": lista_empresas, "ultima_empresa": ULTIMA_EMPRESA}
    return render(request, "cheques/novo.html", context)


def get_data(request, id):
    if request.method == "GET":
        obj = Empresa.objects.get(id=id)
        print("aqui: " + str(obj.conta))
        data_dict = {"conta": obj.conta, "banco": obj.banco, "agencia": obj.agencia}
        data = simplejson.dumps(data_dict)
        return HttpResponse(data, content_type="application/json")


@login_required
def cadastro(request):
    lista_cheques = Cheque.objects.all()
    lista_empresas = Empresa.objects.all()
    context = {
        "lista_cheques": lista_cheques,
        "lista_empresas": lista_empresas,
    }
    return render(request, "cheques/cadastro.html", context)


@login_required
def hist(request):
    lista_cheques = Cheque.objects.all()
    lista_empresas = Empresa.objects.all()
    lista_historico = Historico.objects.all().order_by("dt_comp_excl")
    context = {
        "lista_cheques": lista_cheques,
        "lista_empresas": lista_empresas,
        "lista_historico": lista_historico,
    }
    return render(request, "cheques/hist.html", context)


@login_required
def add(request):
    if request.method == "GET":
        print("get")
        return HttpResponse("get")
    elif request.method == "POST":
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
        }

        cheque_instance = Cheque.objects.create(**itens)
        ULTIMA_EMPRESA = Empresa.objects.get(pk=request.POST.get("empresa"))
        return redirect("index")


@login_required
def edit(request):
    if request.method == "GET":
        print("get")
        return HttpResponse("get")
    elif request.method == "POST":
        id = request.POST.get("id")
        print(id)
        cheque_instance = Cheque.objects.get(id=id)
        itens = {
            "nr_cheque": request.POST.get("nr_cheque"),
            "valor": request.POST.get("valor"),
            "empresa": Empresa.objects.get(pk=request.POST.get("empresa")),
            "banco": request.POST.get("banco"),
            "agencia": request.POST.get("agencia"),
            "conta": request.POST.get("conta"),
            "dt_futura": request.POST.get("dt_futura"),
            "destinatario": request.POST.get("destinatario"),
        }

        cheque_instance = Cheque.objects.update(**itens)
        return redirect("index")


@login_required
def addcadastro(request):
    if request.method == "GET":
        print("get")
        return HttpResponse("get")
    elif request.method == "POST":
        print("request: " + str(request))
        itens = {
            "nome": request.POST.get("nome"),
            "cpfpj": request.POST.get("cpfpj"),
            "banco": request.POST.get("banco"),
            "agencia": request.POST.get("agencia"),
            "conta": request.POST.get("conta"),
            "dt_record": datetime.datetime.today(),
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
        }
        historico_instance = Historico.objects.create(**hist)
        historico_instance.save()
        instance.delete()
        return redirect("index")


@login_required
def editar(request, id=None):
    if request.method == "GET":
        lista_cheques = Cheque.objects.all()
        lista_empresas = Empresa.objects.all()
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
    else:
        return redirect("editar")

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
