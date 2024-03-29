# Generated by Django 4.2.6 on 2023-10-28 23:24

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Bable', '0002_alter_anon_applied_dictionaries'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentLocations',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_top', models.IntegerField(default=0)),
                ('from_left', models.IntegerField(default=0)),
                ('comments', models.ManyToManyField(default=None, to='Bable.comment')),
            ],
        ),
        migrations.CreateModel(
            name='Votings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.CharField(default='', max_length=15)),
                ('creation_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('author', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='Bable.author')),
                ('sponsor', models.ManyToManyField(default=None, to='Bable.sponsor')),
                ('votes', models.ManyToManyField(default=None, to='Bable.votes')),
            ],
        ),
        migrations.CreateModel(
            name='SearchURL',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=400)),
                ('url', models.URLField(max_length=2000)),
                ('comment_height', models.IntegerField(default=0)),
                ('comment_width', models.IntegerField(default=0)),
                ('sum_comments', models.IntegerField(default=0)),
                ('sum_sponsors', models.IntegerField(default=0)),
                ('viewcount', models.IntegerField(default=0)),
                ('change_count', models.IntegerField(default=0)),
                ('latest_change_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('pub_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('public', models.BooleanField(default=1)),
                ('votes_count', models.IntegerField(default=0)),
                ('cc', models.CharField(default='', max_length=400)),
                ('img', models.URLField(blank=True, default='', max_length=2000)),
                ('stripe_price_id', models.CharField(default='', max_length=100)),
                ('stripe_product_id', models.CharField(default='', max_length=100)),
                ('price', models.IntegerField(default=0)),
                ('monthly', models.BooleanField(default=False)),
                ('allowed_to_view_authors', models.ManyToManyField(default=None, related_name='search_allowed', to='Bable.author')),
                ('comment_locations', models.ManyToManyField(default=None, to='Bable.commentlocations')),
                ('post_allowed', models.ManyToManyField(default=None, related_name='search_allowed_authors', to='Bable.author')),
                ('sponsors', models.ManyToManyField(default=None, to='Bable.sponsor')),
                ('votes', models.ManyToManyField(default=None, to='Bable.votes')),
            ],
        ),
        migrations.AddField(
            model_name='anon',
            name='search_urls',
            field=models.ManyToManyField(default=None, to='Bable.searchurl'),
        ),
        migrations.AddField(
            model_name='post',
            name='search_urls',
            field=models.ManyToManyField(default=None, to='Bable.searchurl'),
        ),
        migrations.AlterField(
            model_name='anon',
            name='past_votes',
            field=models.ManyToManyField(default=None, related_name='past_votes', to='Bable.votings'),
        ),
    ]
