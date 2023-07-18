# Generated by Django 3.2.20 on 2023-07-18 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Bable', '0011_anon_stripe_private_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='anon',
            name='products',
            field=models.ManyToManyField(default=None, to='Bable.Price'),
        ),
        migrations.AddField(
            model_name='price',
            name='name',
            field=models.CharField(default='', max_length=200),
        ),
    ]