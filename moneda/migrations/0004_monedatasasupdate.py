# Generated by Django 2.1.5 on 2019-05-16 17:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moneda', '0003_historicalmoneda'),
    ]

    operations = [
        migrations.CreateModel(
            name='MonedaTasasUpdate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateTimeField(auto_now_add=True, verbose_name='Fecha')),
                ('items', models.TextField(blank=True)),
            ],
        ),
    ]
