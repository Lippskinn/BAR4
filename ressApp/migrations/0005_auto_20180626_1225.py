# Generated by Django 2.0.2 on 2018-06-26 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ressApp', '0004_offer_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offer',
            name='offerImage',
            field=models.ImageField(default='ressApp/static/ressApp/images/beamer.jpg', upload_to='offer_image'),
        ),
    ]
