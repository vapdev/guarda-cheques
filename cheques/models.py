from datetime import datetime
from django.db import models

# Create your models here.
class Empresa(models.Model):
    nome = models.CharField(max_length=50)
    cpfpj = models.CharField(max_length=50, unique=True)
    dt_record = models.DateField()

class Banco(models.Model):
    nome = models.CharField(max_length=50)
    numero = models.CharField(max_length=50, unique=True)
    dt_record = models.DateField()

class Cheque(models.Model):
    nr_cheque = models.CharField(max_length=50, blank=True, null=True)
    nr_conta = models.CharField(max_length=50, blank=True, null=True)
    dt_record = models.DateField(blank=True, null=True)
    dt_futura = models.DateField(blank=True, null=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE,blank=True, null=True)
    banco = models.ForeignKey(Banco, on_delete=models.CASCADE,blank=True, null=True)
    agencia = models.CharField(max_length=50, blank=True, null=True)
    destinatario = models.CharField(max_length=50)
    valor = models.FloatField()
    conta = models.CharField(max_length=10, blank=True, null=True)

class Historico(models.Model):
    nr_cheque = models.CharField(max_length=50, blank=True, null=True)
    nr_conta = models.CharField(max_length=50, blank=True, null=True)
    dt_record = models.DateField(blank=True, null=True)
    dt_futura = models.DateField(blank=True, null=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE,blank=True, null=True)
    banco = models.ForeignKey(Banco, on_delete=models.CASCADE,blank=True, null=True)
    agencia = models.CharField(max_length=50, blank=True, null=True)
    destinatario = models.CharField(max_length=50, null=True)
    valor = models.FloatField(null=True)
    conta = models.CharField(max_length=10, blank=True, null=True)
    dt_comp_excl = models.DateField(blank=True, null=True)
    compensado = models.BooleanField()