from django.contrib import admin
from .models import Cheque, Banco, Empresa, Historico
# Register your models here.
admin.site.register([Cheque, Banco, Empresa, Historico])