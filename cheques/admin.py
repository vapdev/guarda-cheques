from django.contrib import admin
from .models import Cheque, Empresa, Historico

# Register your models here.
admin.site.register([Cheque, Empresa, Historico])
