# Generated by Django 2.1.5 on 2019-05-16 18:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('documento', '0016_auto_20190516_1711'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documento',
            name='persona',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, to='persona.Persona', verbose_name='Persona'),
        ),
        migrations.AlterField(
            model_name='historicaldocumento',
            name='persona',
            field=models.ForeignKey(blank=True, db_constraint=False, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='persona.Persona', verbose_name='Persona'),
        ),
    ]
