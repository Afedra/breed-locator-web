# Generated by Django 2.1.5 on 2019-04-15 17:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Breed',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('breed_type', models.CharField(choices=[('ANKOLE', 'Ankole'), ('JERSEY', 'Jersey'), ('ZEBU', 'Zebu'), ('FRESIAN', 'Fresian'), ('UNKNOWN', 'Unknown')], default='UNKNOWN', max_length=50)),
                ('breed', models.TextField(max_length=255)),
                ('matches', models.IntegerField(default=0)),
                ('comments', models.IntegerField(default=0)),
                ('sex', models.CharField(choices=[('MALE', 'Male'), ('FEMALE', 'Female')], default='MALE', max_length=8)),
                ('photo', models.ImageField(blank=True, max_length=500, null=True, upload_to='breeds', verbose_name='photo')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='breeds.Breed')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Breed',
                'verbose_name_plural': 'Breed',
                'ordering': ('-date',),
            },
        ),
    ]
