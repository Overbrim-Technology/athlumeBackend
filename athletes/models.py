from django.conf import settings
from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

from organizations.models import Organization


# A robust regex for Unicode Emojis
emoji_validator = RegexValidator(
    regex=r'^[\U00010000-\U0010ffff\u2600-\u26ff\u2700-\u27bf]+$',
    message="This field must contain only emojis."
)


# Create your models here.
class Person(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone = models.CharField(max_length=15)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Athlete(Person):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    # Make fields optional at registration/onboarding so user can supply
    # only core information (first/last/email/phone) during signup.
    age = models.IntegerField(null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    sport = models.CharField(max_length=250, blank=True, null=True)
    school = models.CharField(max_length=50, blank=True, null=True)
    graduation_year = models.IntegerField(null=True, blank=True)
    coach_name = models.CharField(max_length=100, blank=True, null=True)
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='athletes'
    )

    def __str__(self):
        parts = [self.first_name, self.last_name]
        name = " ".join([p for p in parts if p])
        extras = []
        if self.sport:
            extras.append(self.sport)
        if self.organization:
            extras.append(f"{self.organization.name}")
        if extras:
            return f"{name} - {' '.join(extras)}"
        return name
    
class Profile(Athlete):
    # Link to the login account
    profile_picture = models.ImageField(upload_to='profile_picture/', blank=True, null=True)
    banner = models.ImageField(upload_to='profile_banner/', blank=True, null=True)
    youtube = models.CharField(max_length=500, blank=True, null=True)
    facebook = models.CharField(max_length=500, blank=True, null=True)
    x = models.CharField(max_length=500, blank=True, null=True)
    instagram = models.CharField(max_length=500, blank=True, null=True)

class Achievement(models.Model):
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE, null=True, blank=True, related_name='achievements')
    emoji = models.CharField(max_length=10, validators=[emoji_validator],
                             help_text="Add emoji of your achievement (e.g., 🏆, 🎯, ⭐)")
    achievement = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.emoji} {self.achievement}"

class Stat(models.Model):
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE, null=True, blank=True, related_name='stats')
    date = models.DateField()
    event = models.TextField(max_length=100)
    performance = models.TextField(max_length=100)
    highlight = models.TextField(max_length=100)

class Video(models.Model):
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE, null=True, blank=True, related_name='videos')
    url = models.URLField(max_length=500)
