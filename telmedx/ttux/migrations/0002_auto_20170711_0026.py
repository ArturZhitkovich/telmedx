# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-11 00:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ttux', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mobilecam',
            name='email',
            field=models.EmailField(default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='mobilecam',
            name='first_name',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='mobilecam',
            name='last_name',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='mobilecam',
            name='phone_number',
            field=models.CharField(default='', max_length=32),
        ),
    ]
