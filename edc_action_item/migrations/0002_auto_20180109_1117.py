# Generated by Django 2.0.1 on 2018-01-09 09:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('edc_action_item', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='actionitem',
            options={'verbose_name': 'Action Item', 'verbose_name_plural': 'Action Items'},
        ),
    ]