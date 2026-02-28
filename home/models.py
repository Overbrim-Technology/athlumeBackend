from PIL import Image
import io

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile
from django.db import models
from django.conf import settings

from athletes.models import Profile

def validate_max_size(value):
    limit = 2 * 1024 * 1024 # 2MB
    if value.size > limit:
        raise ValidationError("File too large. Size should not exceed 2MB.")

class Highlight(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='highlight_images/', 
                              validators=[validate_max_size],
                              blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    published = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    

    def save(self, *args, **kwargs):
        # Only compress if the file is a new upload (is an instance of UploadedFile)
        # If it's already in storage, it will be a 'FieldFile' or 'ImageFieldFile'
        
        if self.image and isinstance(self.image.file, UploadedFile):
            self.image = self._compress_image(self.image)

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


class FeaturedAthlete(models.Model):
    athlete = models.ForeignKey('athletes.Profile', on_delete=models.CASCADE, related_name='featured_entries')
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Featured Athlete'
        verbose_name_plural = 'Featured Athletes'

    def __str__(self):
        return f"Featured: {self.athlete.first_name} {self.athlete.last_name}"