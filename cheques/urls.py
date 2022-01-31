from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("novo/", views.novo, name="novo"),
    path("hist/", views.hist, name="hist"),
    path("bancos/", views.bancos, name="bancos"),
    path("cadastro/", views.cadastro, name="cadastro"),
    path("add/", views.add, name="add"),
    path("addbanco/", views.addbanco, name="addbanco"),
    path("addcadastro/", views.addcadastro, name="addcadastro"),
    path("cadastrodel/<int:id>", views.cadastrodel, name="cadastrodel"),
    path("bancosdel/<int:id>", views.bancosdel, name="bancosdel"),
    path("chequesdel/<int:id>", views.chequesdel, name="chequesdel"),
    path("editar/<int:id>", views.editar, name="editar"),
    path("limparhist/", views.limparhist, name="limparhist"),
    path("compensar/<int:id>", views.compensar, name="compensar"),
    path("edit/", views.edit, name="edit"),
]
