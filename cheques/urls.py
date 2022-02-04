from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("novo/", views.novo, name="novo"),
    path("hist/", views.hist, name="hist"),
    path("cadastro/", views.cadastro, name="cadastro"),
    path("add/", views.add, name="add"),
    path("addcadastro/", views.addcadastro, name="addcadastro"),
    path("cadastrodel/<int:id>", views.cadastrodel, name="cadastrodel"),
    path("chequesdel/<int:id>", views.chequesdel, name="chequesdel"),
    path("editar/<int:id>", views.editar, name="editar"),
    path("limparhist/", views.limparhist, name="limparhist"),
    path("compensar/<int:id>", views.compensar, name="compensar"),
    path("edit/", views.edit, name="edit"),
    path("logout/", views.logout, name="logout"),
    path("get_data/<int:id>", views.get_data, name="get_data"),
    path('pdf_download/', views.DownloadPDF.as_view(), name="pdf_download"),
]
