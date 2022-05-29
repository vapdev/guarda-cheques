from datetime import datetime
from django.db import models
from django.conf import settings

# Create your models here.
class Empresa(models.Model):
    nome = models.CharField(max_length=50)
    cpfpj = models.CharField(max_length=50)
    conta = models.CharField(max_length=50, blank=True, null=True)
    banco = models.CharField(max_length=50, blank=True, null=True)
    agencia = models.CharField(max_length=50, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    dt_record = models.DateField()


class Cheque(models.Model):
    nr_cheque = models.CharField(max_length=50, blank=True, null=True)
    dt_record = models.DateField(blank=True, null=True)
    dt_futura = models.DateField(blank=True, null=True)
    empresa = models.ForeignKey(
        Empresa, on_delete=models.CASCADE, blank=True, null=True
    )
    destinatario = models.CharField(max_length=50)
    valor = models.FloatField()
    banco = models.CharField(max_length=50, blank=True, null=True)
    agencia = models.CharField(max_length=50, blank=True, null=True)
    conta = models.CharField(max_length=10, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)


class Historico(models.Model):
    nr_cheque = models.CharField(max_length=50, blank=True, null=True)
    dt_record = models.DateField(blank=True, null=True)
    dt_futura = models.DateField(blank=True, null=True)
    empresa = models.ForeignKey(
        Empresa, on_delete=models.CASCADE, blank=True, null=True
    )
    banco = models.CharField(max_length=50, blank=True, null=True)
    agencia = models.CharField(max_length=50, blank=True, null=True)
    destinatario = models.CharField(max_length=50, null=True)
    valor = models.FloatField(null=True)
    conta = models.CharField(max_length=10, blank=True, null=True)
    dt_comp_excl = models.DateField(blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    compensado = models.BooleanField()
