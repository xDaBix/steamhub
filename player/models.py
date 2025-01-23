from django.db import models
from django.core.validators import MinLengthValidator
import os
from django.contrib.auth.models import User
from developers.models import Game


class players(models.Model):
    Players_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50, verbose_name='First Name')
    last_name = models.CharField(max_length=50, verbose_name='Last Name')
    username = models.CharField(max_length=6, unique=True, verbose_name='Username')
    email = models.EmailField(unique=True, verbose_name='Email')
    failed_attempts = models.IntegerField(default=0)
    lockout_time = models.DateTimeField(null=True, blank=True)
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
    profile_image = models.ImageField(
    upload_to='profile_images/',
    default='C:\\Users\\asus\\Documents\\steam\\player\\static\\player\\images\\profileimages\\profile-user.png',
    null=True,
    blank=True
    )
    def __str__(self):
        return self.username
    
class Payment(models.Model):
    order_id = models.CharField(max_length=100, unique=True)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    payment_status = models.CharField(max_length=50, default="Pending")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='payments')

    def __str__(self):
        return f"Payment {self.order_id} - {self.payment_status}"
    

class Library(models.Model):
    player = models.ForeignKey(players, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    purchased_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player.username} - {self.game.title}"
    


class Friendship(models.Model):
    player1 = models.ForeignKey('players', on_delete=models.CASCADE, related_name='friend_requests_sent')
    player2 = models.ForeignKey('players', on_delete=models.CASCADE, related_name='friend_requests_received')
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')])

    def __str__(self):
        return f"{self.player1} -> {self.player2} ({self.status})"
