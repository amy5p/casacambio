# Generated by Django 2.2.3 on 2019-09-29 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prestamo', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cuenta',
            name='tags',
            field=models.TextField(blank=True, editable=False),
        ),
        migrations.AlterField(
            model_name='prestamo',
            name='tags',
            field=models.TextField(blank=True, editable=False),
        ),
        migrations.AlterField(
            model_name='transaccion',
            name='tags',
            field=models.TextField(blank=True, editable=False),
        ),
    ]
