# Generated by Django 3.2.24 on 2024-06-10 11:12

import datetime
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Bable', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserViews',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('view_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('page_view', models.CharField(default='', max_length=200)),
                ('previous_view_id', models.CharField(default='', max_length=144)),
                ('previous_page', models.CharField(default='', max_length=200)),
                ('previous_view_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('previous_view_time_between_pages', models.DurationField(default=datetime.timedelta(seconds=1))),
                ('anon', models.OneToOneField(default=None, on_delete=django.db.models.deletion.PROTECT, to='Bable.anon')),
            ],
        ),
        migrations.AddField(
            model_name='pageviews',
            name='user_views',
            field=models.ManyToManyField(default=None, to='Bable.UserViews'),
        ),
    ]
