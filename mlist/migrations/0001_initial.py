# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-10-13 05:53
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='IMDBMovie',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID')),
                ('imdb_id', models.CharField(
                    db_index=True,
                    max_length=255,
                    unique=True)),
                ('title', models.CharField(max_length=255)),
                ('year', models.IntegerField(null=True)),
                ('rated', models.CharField(max_length=255, null=True)),
                ('released', models.DateField(null=True)),
                ('runtime', models.CharField(max_length=255, null=True)),
                ('director', models.TextField(null=True)),
                ('writer', models.TextField(null=True)),
                ('actors', models.TextField(null=True)),
                ('plot', models.TextField(null=True)),
                ('votes', models.IntegerField(null=True)),
                ('rating', models.FloatField(null=True)),
                ('genre', models.TextField(null=True)),
                ('poster_url', models.CharField(max_length=255, null=True)),
                ('update_date', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('imdb_id', models.CharField(
                    blank=True,
                    max_length=200,
                    null=True)),
            ],
            options={
                'permissions': (('update_movie', 'Can update movie'),),
            },
        ),
        migrations.CreateModel(
            name='MovieInCollection',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('collection', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='mlist.Collection')),
                ('movie', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='mlist.Movie')),
                ('tags', taggit.managers.TaggableManager(
                    blank=True,
                    help_text='A comma-separated list of tags.',
                    through='taggit.TaggedItem',
                    to='taggit.Tag',
                    verbose_name='Tags')),
            ],
        ),
        migrations.CreateModel(
            name='TMDBMovie',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID')),
                ('imdb_id', models.CharField(
                    db_index=True,
                    max_length=255,
                    unique=True)),
                ('tmdb_id', models.CharField(max_length=255, unique=True)),
                ('original_title', models.CharField(max_length=255)),
                ('title', models.CharField(max_length=255)),
                ('popularity', models.IntegerField(null=True)),
                ('adult', models.NullBooleanField()),
                ('spoken_languages', models.CharField(max_length=255)),
                ('homepage', models.TextField(null=True)),
                ('overview', models.TextField(null=True)),
                ('vote_average', models.IntegerField(null=True)),
                ('vote_count', models.IntegerField(null=True)),
                ('runtime', models.IntegerField(null=True)),
                ('budget', models.IntegerField(null=True)),
                ('revenue', models.IntegerField(null=True)),
                ('genres', models.TextField(null=True)),
                ('production_companies', models.TextField(null=True)),
                ('productions_countries', models.TextField(null=True)),
                ('poster_path', models.TextField(null=True)),
                ('backdrop_path', models.TextField(null=True)),
                ('tagline', models.TextField()),
                ('update_date', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name='collection',
            name='movies',
            field=models.ManyToManyField(
                blank=True,
                through='mlist.MovieInCollection',
                to='mlist.Movie'),
        ),
        migrations.AddField(
            model_name='collection',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL),
        ),
    ]
