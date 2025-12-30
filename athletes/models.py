from django.conf import settings
from django.db import models
from organizations.models import Organization

# Create your models here.
class Person(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone = models.CharField(max_length=15)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Athlete(Person):
    # Link to the login account
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    age = models.IntegerField()
    bio = models.TextField()
    sport = models.CharField(max_length=50)
    school = models.CharField(max_length=50)
    graduation_year = models.IntegerField()
    coach_name = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to='profile_picture/', blank=True, null=True)
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='athletes'
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.sport} ({self.school})"
    