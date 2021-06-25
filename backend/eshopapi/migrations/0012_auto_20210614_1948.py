# Generated by Django 3.1.7 on 2021-06-14 16:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eshopapi', '0011_product_shops'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productinfo',
            name='shop',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='shops', to='eshopapi.shop', verbose_name='Магазин'),
        ),
    ]
