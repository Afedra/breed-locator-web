# Generated by Django 2.1.5 on 2019-03-29 17:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('breeds', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='breed',
            old_name='post',
            new_name='breed',
        ),
        migrations.AlterField(
            model_name='breed',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='breeds.Breed'),
        ),
    ]
