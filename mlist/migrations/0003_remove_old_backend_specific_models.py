# Generated by Django 2.1.2 on 2019-08-31 12:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mlist', '0002_backend_movie'),
    ]

    operations = [
        migrations.DeleteModel(
            name='IMDBMovie',
        ),
        migrations.DeleteModel(
            name='TMDBMovie',
        ),
    ]
