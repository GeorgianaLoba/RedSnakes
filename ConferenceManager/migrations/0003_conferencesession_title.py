# Generated by Django 3.0.6 on 2020-05-21 19:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ConferenceManager', '0002_auto_20200521_2112'),
    ]

    operations = [
        migrations.AddField(
            model_name='conferencesession',
            name='title',
            field=models.CharField(default=None, max_length=255),
            preserve_default=False,
        ),
    ]