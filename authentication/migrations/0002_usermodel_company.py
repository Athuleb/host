# Generated by Django 3.1.12 on 2024-12-06 05:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usermodel',
            name='company',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
