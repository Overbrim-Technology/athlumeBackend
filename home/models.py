from django.db import models
from django.conf import settings


class Highlight(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='highlight_images/', blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    published = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class FeaturedAthlete(models.Model):
    from athletes.models import Athlete

    athlete = models.ForeignKey('athletes.Athlete', on_delete=models.CASCADE, related_name='featured_entries')
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