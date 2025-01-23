# Generated by Django 5.1 on 2024-11-29 15:54

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Developer',
            fields=[
                ('did', models.AutoField(primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=50, verbose_name='First Name')),
                ('last_name', models.CharField(max_length=50, verbose_name='Last Name')),
                ('username', models.CharField(max_length=6, unique=True, verbose_name='Username')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Email')),
                ('password', models.CharField(max_length=100, validators=[django.core.validators.MinLengthValidator(8)], verbose_name='Password')),
                ('contact', models.CharField(max_length=10, verbose_name='Contact')),
                ('date_of_birth', models.DateField(verbose_name='Date of Birth')),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], max_length=10, verbose_name='Status')),
            ],
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('game_id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=100)),
                ('game_type', models.CharField(choices=[('Action', 'Action'), ('Adventure', 'Adventure'), ('Puzzle', 'Puzzle'), ('RPG', 'Role-Playing Game'), ('Sports', 'Sports'), ('Strategy', 'Strategy')], max_length=50)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=6)),
                ('release_date', models.DateField(default=django.utils.timezone.now)),
                ('version', models.IntegerField(default=1)),
                ('game_file', models.FileField(upload_to='game_files/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('is_approved', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending', max_length=10)),
                ('developer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='games', to='developers.developer')),
            ],
        ),
        migrations.CreateModel(
            name='GameImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='game_images/')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='developers.game')),
            ],
        ),
    ]
