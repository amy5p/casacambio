# Generated by Django 2.2 on 2019-05-05 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('almacen', '0002_auto_20190505_0935'),
    ]

    operations = [
        migrations.AlterField(
            model_name='almacen',
            name='tags',
            field=models.TextField(blank=True, editable=False),
        ),
    ]
