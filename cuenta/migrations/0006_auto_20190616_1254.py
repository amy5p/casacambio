# Generated by Django 2.1.5 on 2019-06-16 12:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cuenta', '0005_auto_20190612_1759'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cuenta',
            old_name='index',
            new_name='orden',
        ),
        migrations.RenameField(
            model_name='historicalcuenta',
            old_name='index',
            new_name='orden',
        ),
    ]
