# Generated by Django 4.0.1 on 2022-01-28 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cheques', '0012_alter_banco_dt_record_alter_cheque_dt_record_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historico',
            name='dt_comp_excl',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
