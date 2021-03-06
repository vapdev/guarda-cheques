# Generated by Django 4.0.1 on 2022-01-27 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cheques', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Banco',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=50)),
                ('numero', models.CharField(max_length=50, unique=True)),
                ('dt_record', models.DateField()),
            ],
        ),
        migrations.DeleteModel(
            name='User',
        ),
        migrations.RenameField(
            model_name='cheque',
            old_name='cd_empresa',
            new_name='empresa',
        ),
        migrations.RenameField(
            model_name='empresa',
            old_name='cnpj',
            new_name='cpfpj',
        ),
    ]
