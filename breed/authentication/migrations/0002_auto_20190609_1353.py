# Generated by Django 2.1.5 on 2019-06-09 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='job_title',
            field=models.CharField(blank=True, choices=[('FARMER', 'Farmer'), ('DOCTOR', 'Doctor')], max_length=100, null=True),
        ),
    ]