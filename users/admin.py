from django.contrib import admin
from rest_framework.authtoken.models import Token
from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken, EmailAddress

from .models import User

# Unregister allauth social models
try:
    admin.site.unregister(SocialAccount)
    admin.site.unregister(SocialApp)
    admin.site.unregister(SocialToken)
    admin.site.unregister(EmailAddress)
    admin.site.unregister(Token)
except admin.sites.NotRegistered:
    pass


# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    model = User
    list_display = ('email', 'first_name', 'last_name', 'role')
    search_fields = ('email', 'first_name', 'last_name')
