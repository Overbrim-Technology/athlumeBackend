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

    def role(self):
        # This hits the DB once, or 0 times if you used prefetch_related
        group_names = {g.name for g in self.groups.all()}

        if hasattr(self, 'athlete') or 'Athlete' in group_names:
            return 'athlete'

        if hasattr(self, 'organization') or 'Organization Owner' in group_names:
            return 'organization'

        return 'user'