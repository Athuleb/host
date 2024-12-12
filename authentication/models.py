from django.contrib.auth.models import AbstractUser
from django.db import models

class UserModel(AbstractUser):

    user_type = models.CharField(
        max_length=50,
        choices=[('personal', 'Personal User'), ('business', 'Business User')],
        null=True, blank=True
    )
    dob = models.DateField(null=True, blank=True, verbose_name="Date of Birth")
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female')], null=True, blank=True)
    mobile = models.CharField(max_length=15, null=True, blank=True, verbose_name="Mobile Number")
    state = models.CharField(max_length=50, null=True, blank=True)
    district = models.CharField(max_length=50, null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)
    company = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.username
