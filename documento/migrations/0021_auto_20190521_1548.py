# Generated by Django 2.1.5 on 2019-05-21 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documento', '0020_auto_20190520_1719'),
    ]

    operations = [
        migrations.AddField(
            model_name='documento',
            name='tasa_entrada_para_venta_del_dia',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=5, verbose_name='Tasa de venta del día'),
        ),
        migrations.AddField(
            model_name='historicaldocumento',
            name='tasa_entrada_para_venta_del_dia',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=5, verbose_name='Tasa de venta del día'),
        ),
    ]
