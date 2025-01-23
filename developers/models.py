from django.db import models
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import User
from django.utils import timezone
import os

class Developer(models.Model):
    did = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50, verbose_name='First Name')
    last_name = models.CharField(max_length=50, verbose_name='Last Name')
    username = models.CharField(max_length=6, unique=True, verbose_name='Username')
    email = models.EmailField(unique=True, verbose_name='Email')
    password = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(8)],
        verbose_name='Password'
    )
    contact = models.CharField(max_length=10, verbose_name='Contact')
    date_of_birth = models.DateField(verbose_name='Date of Birth')
    status = models.CharField(
        max_length=10,
        choices=[('active', 'Active'), ('inactive', 'Inactive')],
        verbose_name='Status'
    )


class Game(models.Model):
    GAMETYPE_CHOICES = [
        ('Action', 'Action'),
        ('Adventure', 'Adventure'),
        ('Puzzle', 'Puzzle'),
        ('RPG', 'Role-Playing Game'),
        ('Sports', 'Sports'),
        ('Strategy', 'Strategy'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    game_id = models.AutoField(primary_key=True)  
    developer = models.ForeignKey('Developer', on_delete=models.CASCADE, related_name='games')
    title = models.CharField(max_length=100)
    game_type = models.CharField(max_length=50, choices=GAMETYPE_CHOICES)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    release_date = models.DateField(default=timezone.now)
    version = models.IntegerField(default=1)
    game_file = models.FileField(upload_to='game_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return self.title

class GameImage(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='game_images/')

    def __str__(self):
        return f"Image for {self.game.title}"