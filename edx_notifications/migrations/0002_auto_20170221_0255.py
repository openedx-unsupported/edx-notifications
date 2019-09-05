# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('edx_notifications', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='sqlusernotificationpreferences',
            unique_together=set([('user_id', 'preference')]),
        ),
    ]
