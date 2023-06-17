# Generated by Django 4.1.5 on 2023-06-17 04:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Bable', '0004_alter_votes_the_vote_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='votes_source',
            name='the_vote_name',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='votename', to='Bable.word_source'),
        ),
        migrations.AlterField(
            model_name='votes_source',
            name='the_vote_style',
            field=models.ManyToManyField(default=None, related_name='votestyle', to='Bable.word_source'),
        ),
    ]
