# Generated by Django 2.1.5 on 2019-06-08 21:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_configuracionfacturacion_creacion'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='configuracionfacturacion',
            name='moneda_entrada_predeterminada',
        ),
        migrations.RemoveField(
            model_name='configuracionfacturacion',
            name='moneda_salida_predeterminada',
        ),
    ]