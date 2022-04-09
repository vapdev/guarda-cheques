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
from django.db import models

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

        if request.GET.get("empresa") and request.GET.get("empresa") != "0":
            empresa = Empresa.objects.get(id=request.GET.get("empresa"))
        print(type(query["dt_liberacao_ini"]))
        lista_cheques = Cheque.objects.filter(user=query["user"]).order_by("dt_futura")
        dt_liberacao_ini = request.GET.get("dt_liberacao_ini")
        dt_liberacao_fim = request.GET.get("dt_liberacao_fim")
        lista_filtros = []
        if query["dt_liberacao_ini"] and query["dt_liberacao_fim"]:
            lista_cheques = Cheque.objects.filter(
                dt_futura__gte=query["dt_liberacao_ini"],
                dt_futura__lte=query["dt_liberacao_fim"],
            ).order_by("dt_futura")
            print('lista: '+str(query["dt_liberacao_ini"]))
            unformatted_ini = str(query["dt_liberacao_ini"]).split("-")
            ano = unformatted_ini[0]
            mes = unformatted_ini[1]
            dia = unformatted_ini[2]
            formatted_ini = f'{dia}/{mes}/{ano}'

            unformatted_fim = str(query["dt_liberacao_fim"]).split("-")
            ano = unformatted_fim[0]
            mes = unformatted_fim[1]
            dia = unformatted_fim[2]
            formatted_fim = f'{dia}/{mes}/{ano}'
            print (ano)
            lista_filtros.append(f'Relatório dos cheques compensados entre {formatted_ini} e {formatted_fim}')
        

        elif query["dt_liberacao_ini"] and not query["dt_liberacao_fim"]:
            lista_cheques = Cheque.objects.filter(dt_futura__gte=query["dt_liberacao_ini"]).order_by("dt_futura")
            lista_filtros.append(f'Relatório dos cheques compensados a partir de {query["dt_liberacao_ini"]}')
            unformatted_ini = str(query["dt_liberacao_ini"]).split("-")
            ano = unformatted_ini[0]
            mes = unformatted_ini[1]
            dia = unformatted_ini[2]
            formatted_ini = f'{dia}/{mes}/{ano}'

        elif query["dt_liberacao_fim"] and not query["dt_liberacao_ini"]:
            lista_cheques = Cheque.objects.filter(dt_futura__lte=query["dt_liberacao_fim"]).order_by("dt_futura")
            lista_filtros.append(f'Relatório dos cheques compensados até {query["dt_liberacao_fim"]}')
            unformatted_fim = str(query["dt_liberacao_fim"]).split("-")
            ano = unformatted_fim[0]
            mes = unformatted_fim[1]
            dia = unformatted_fim[2]
            formatted_fim = f'{dia}/{mes}/{ano}'
        # if query["dt_cadastro_ini"] and query["dt_cadastro_fim"]:
        #     lista_cheques = Cheque.objects.filter(
        #         dt_futura__gte=query["dt_cadastro_ini"],
        #         dt_futura__lte=query["dt_cadastro_fim"],
        #     )
        # elif query["dt_cadastro_ini"] and not query["dt_cadastro_fim"]:
        #     lista_cheques = Cheque.objects.filter(dt_futura__gte=query["dt_cadastro_ini"])
        # elif query["dt_cadastro_fim"] and not query["dt_cadastro_ini"]:
        #     lista_cheques = Cheque.objects.filter(dt_futura__lte=query["dt_cadastro_fim"])

        if query["empresa"] and query["empresa"] != "0":
            lista_cheques = Cheque.objects.filter(empresa_id=int(query["empresa"])).order_by("dt_futura")
            lista_filtros.append(f'Relatório dos cheques da empresa {empresa.nome}')

        if query["destinatario"] and query["empresa"]=="0":
            lista_cheques = Cheque.objects.filter(destinatario__icontains=query["destinatario"]).order_by("dt_futura")
            lista_filtros.append(f'Relatório dos cheques de destinatário {query["destinatario"]}')

        elif query["destinatario"] and query["empresa"] and query["empresa"] != "0":
            lista_cheques = Cheque.objects.filter(destinatario__icontains=query["destinatario"]).filter(empresa_id=int(query["empresa"])).order_by("dt_futura")
            lista_filtros.append(f'Relatório dos cheques de destinatário {query["destinatario"]} confeccionados pela empresa {query["empresa"]}')
            
        context = {"lista_cheques": lista_cheques,
                   "valor_total": lista_cheques.aggregate(Sum('valor'))['valor__sum']}
        
        if lista_filtros:
            context = {"lista_cheques": lista_cheques,
                    "lista_filtros": lista_filtros[0],
                    "valor_total": lista_cheques.aggregate(Sum('valor'))['valor__sum']}
        
        print(lista_filtros)

        pdf = render_to_pdf('cheques/pdf_template.html', context)
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"relatorio{datetime.datetime.today().strftime('%d-%m-%Y-%H:%M:%S')}.pdf" 
        content = "attachment; filename=%s" %(filename)
        response['Content-Disposition'] = content
        return response



def home(request):
    return redirect("index")


def logout(request):
    django_logout(request)
    return redirect("index")


@login_required
def index(request):
    user = request.user.id
    lista_empresas = Empresa.objects.filter(user=user)
    lista_cheques = Cheque.objects.filter(user=user).order_by("dt_futura")

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
        "user": request.user.id
    }

    if query["dt_liberacao_ini"] and query["dt_liberacao_fim"]:
        lista_cheques = Cheque.objects.filter(
            dt_futura__gte=query["dt_liberacao_ini"],
            dt_futura__lte=query["dt_liberacao_fim"],
            user=query["user"]
        )
    elif query["dt_liberacao_ini"] and not query["dt_liberacao_fim"]:
        lista_cheques = Cheque.objects.filter(dt_futura__gte=query["dt_liberacao_ini"], user=query["user"])
    elif query["dt_liberacao_fim"] and not query["dt_liberacao_ini"]:
        lista_cheques = Cheque.objects.filter(dt_futura__lte=query["dt_liberacao_fim"], user=query["user"])

    if query["dt_cadastro_ini"] and query["dt_cadastro_fim"]:
        lista_cheques = Cheque.objects.filter(
            dt_futura__gte=query["dt_cadastro_ini"],
            dt_futura__lte=query["dt_cadastro_fim"],
            user=query["user"]
        )
    elif query["dt_cadastro_ini"] and not query["dt_cadastro_fim"]:
        lista_cheques = Cheque.objects.filter(dt_futura__gte=query["dt_cadastro_ini"], user=query["user"])
    elif query["dt_cadastro_fim"] and not query["dt_cadastro_ini"]:
        lista_cheques = Cheque.objects.filter(dt_futura__lte=query["dt_cadastro_fim"], user=query["user"])

    if query["empresa"] and query["empresa"] != "0":
        lista_cheques = Cheque.objects.filter(empresa_id=int(query["empresa"]), user=query["user"])

    if query["destinatario"] and query["empresa"]=="0":
        lista_cheques = Cheque.objects.filter(destinatario__icontains=query["destinatario"], user=query["user"])
    elif query["destinatario"] and query["empresa"] and query["empresa"] != "0":
        lista_cheques = Cheque.objects.filter(destinatario__icontains=query["destinatario"], empresa_id=int(query["empresa"]), user=query["user"])

    if query["nr_cheque"]:
        lista_cheques = Cheque.objects.filter(nr_cheque=query["nr_cheque"], user=query["user"])

    context = {"lista_cheques": lista_cheques, "lista_empresas": lista_empresas}
    return render(request, "cheques/index.html", context)


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
    lista_empresas = Empresa.objects.filter(user=user)
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
        print("get")
        return HttpResponse("get")
    elif request.method == "POST":
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
    else:
        return redirect("editar")


@login_required
def edit(request):
    if request.method == "GET":
        print("get")
        return HttpResponse("get")
    elif request.method == "POST":
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
