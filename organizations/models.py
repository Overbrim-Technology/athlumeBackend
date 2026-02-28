from PIL import Image
import io

from django.core.exceptions import ValidationError
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile
from django.db import models


def validate_max_size(value):
    limit = 2 * 1024 * 1024 # 2MB
    if value.size > limit:
        raise ValidationError("File too large. Size should not exceed 2MB.")

# Create your models here.
class Organization(models.Model):
    # Link to the admin account for this specific org/school
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    logo = models.ImageField(upload_to='org_logos/', 
                             validators=[validate_max_size],
                             blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Only compress if the file is a new upload (is an instance of UploadedFile)
        # If it's already in storage, it will be a 'FieldFile' or 'ImageFieldFile'
        
        if self.logo and isinstance(self.logo.file, UploadedFile):
            self.logo = self._compress_image(self.logo)

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


class School(Organization):
    principal_name = models.CharField(max_length=100)
    established_year = models.IntegerField()

    def __str__(self):
        return f"{self.name} (Established: {self.established_year})"