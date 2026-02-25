from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):

    # We add the "nicknames" here to avoid the clash we saw earlier
    groups = models.ManyToManyField(
        'auth.Group',
        related_name="custom_user_groups",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name="custom_user_permissions",
        blank=True
    )

    @property
    def role(self):
        # We use hasattr to check for relationships without importing the models
        if hasattr(self, 'athlete'):
            return 'athlete'
        if hasattr(self, 'organization'):
            return 'organization'
        return 'user'