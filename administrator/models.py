from django.db import models

# Create your models here.

class admin_user(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=18)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    OTP = models.CharField(max_length=6)

    def __str__(self):
        return self.username
