# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-14 18:17
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import re
import website.qa.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer_text', models.TextField()),
                ('pub_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date published')),
                ('is_correct', models.BooleanField(default=False)),
                ('rating', models.IntegerField(default=0)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to=settings.AUTH_USER_MODEL)),
                ('down_votes', models.ManyToManyField(related_name='down_answer_votes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-rating', '-pub_date'],
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('header', models.CharField(max_length=255)),
                ('pub_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date published')),
                ('text', models.TextField()),
                ('tags', models.CharField(max_length=255, validators=[website.qa.validators.validate_max_list_length, django.core.validators.RegexValidator(re.compile('^(?:\\w+((?:\\s*\\,\\s*)|(?:\\w*)|(?:\\s*$)))+$', 32), code='invalid', message='Enter tags (alphanumeric characters and the underscore are only allowed) separated by commas.')])),
                ('rating', models.IntegerField(default=0)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to=settings.AUTH_USER_MODEL)),
                ('down_votes', models.ManyToManyField(related_name='down_question_votes', to=settings.AUTH_USER_MODEL)),
                ('up_votes', models.ManyToManyField(related_name='up_question_votes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.SlugField(unique=True)),
                ('question', models.ManyToManyField(related_name='related_tags', to='qa.Question')),
            ],
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='qa.Question'),
        ),
        migrations.AddField(
            model_name='answer',
            name='up_votes',
            field=models.ManyToManyField(related_name='up_answer_votes', to=settings.AUTH_USER_MODEL),
        ),
    ]
