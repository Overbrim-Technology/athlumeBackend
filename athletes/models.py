from PIL import Image
import io

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db import models

from organizations.models import Organization


# A robust regex for Unicode Emojis
emoji_validator = RegexValidator(
    regex=r'^[\U00010000-\U0010ffff\u2600-\u26ff\u2700-\u27bf]+$',
    message="This field must contain only emojis."
)

def validate_max_size(value):
    limit = 2 * 1024 * 1024 # 2MB
    if value.size > limit:
        raise ValidationError("File too large. Size should not exceed 2MB.")


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
    profile_picture = models.ImageField(upload_to='profile_picture/',   
                                        validators=[validate_max_size],
                                        blank=True, null=True)
    banner = models.ImageField(upload_to='profile_banner/', 
                               validators=[validate_max_size],
                               blank=True, null=True)
    youtube = models.CharField(max_length=500, blank=True, null=True)
    facebook = models.CharField(max_length=500, blank=True, null=True)
    x = models.CharField(max_length=500, blank=True, null=True)
    instagram = models.CharField(max_length=500, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Only compress if the file is a new upload (is an instance of UploadedFile)
        # If it's already in storage, it will be a 'FieldFile' or 'ImageFieldFile'
        
        if self.profile_picture and isinstance(self.profile_picture.file, UploadedFile):
            self.profile_picture = self._compress_image(self.profile_picture)

        if self.banner and isinstance(self.banner.file, UploadedFile):
            self.banner = self._compress_image(self.banner)

        super().save(*args, **kwargs)

    def _compress_image(self, image_field):
        img = Image.open(image_field)
        
        # Preserve original format (PNG, JPEG, etc.)
        original_format = img.format
        
        # Resize if necessary
        if img.width > 1200 or img.height > 1200:
            img.thumbnail((1200, 1200))
        
        buffer = io.BytesIO()
        
        # If it's a PNG, you might want to keep it as PNG to preserve transparency
        # or convert to JPEG for maximum space saving.
        save_format = 'JPEG' if original_format != 'PNG' else 'PNG'
        
        img.save(buffer, format=save_format, quality=70 if save_format == 'JPEG' else None)
        
        # Return a new ContentFile to be assigned back to the field
        return ContentFile(buffer.getvalue(), name=image_field.name)


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
