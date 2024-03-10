from django.db import models
from django.contrib.auth.models import User

class GovernmentData(models.Model):
    aadhar_number = models.BigIntegerField(unique=True)
    mobile_number = models.BigIntegerField(unique=True)
    age = models.PositiveIntegerField()

    def __str__(self):
        return f"Aadhar: {self.aadhar_number}, Mobile: {self.mobile_number}, Age: {self.age}"

class YourModel(models.Model):
    id = models.BigAutoField(primary_key=True)  # Explicitly define primary key

    # Your other fields here

class PrimaryVoterDatabase(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    unique_address = models.CharField(max_length=255)
    aadhar_number = models.CharField(max_length=12, unique=True)
    mobile_number = models.CharField(max_length=10)
    primary_pass = models.CharField(max_length=128)

class SecondaryVoterDatabase(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    unique_address = models.CharField(max_length=255)
    aadhar_number = models.CharField(max_length=12, unique=True)
    mobile_number = models.CharField(max_length=10)
    secondary_pass = models.CharField(max_length=128)

    def __str__(self):
        return f"Voter Data: Aadhar - {self.aadhar_number}"

class Official(models.Model):
    FULLName = models.CharField(max_length=100)
    Username = models.CharField(max_length=50, unique=True)
    Email = models.EmailField(unique=True)
    Aadhar_Number = models.CharField(max_length=12, unique=True)
    Password = models.CharField(max_length=100)
    
    def __str__(self):
        return self.Username