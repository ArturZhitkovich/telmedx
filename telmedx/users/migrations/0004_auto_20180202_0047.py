# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-02-02 00:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20180131_0133'),
    ]

    operations = [
        migrations.RenameField(
            model_name='telmedxgroupprofile',
            old_name='contact',
            new_name='contact_email',
        ),
        migrations.AddField(
            model_name='telmedxgroupprofile',
            name='contact_name',
            field=models.CharField(default='asdsad', max_length=128),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='telmedxgroupprofile',
            name='contact_phone',
            field=models.CharField(default='asdad', max_length=64),
            preserve_default=False,
        ),
    ]
