# Generated by Django 2.1.5 on 2019-06-09 17:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('documento', '0024_auto_20190609_1701'),
        ('base', '0008_configuracionfacturacion_moneda_salida_predeterminada'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuracionfacturacion',
            name='tipo_documento_predeterminado',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='documento.DocumentoTipo', verbose_name='Tipo de documento predeterminado'),
        ),
    ]