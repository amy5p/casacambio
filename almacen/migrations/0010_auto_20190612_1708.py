# Generated by Django 2.2.1 on 2019-06-12 17:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('almacen', '0009_auto_20190612_1650'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='almacen',
            name='tipo_documento_predeterminado',
        ),
        migrations.RemoveField(
            model_name='historicalalmacen',
            name='tipo_documento_predeterminado',
        ),
    ]
