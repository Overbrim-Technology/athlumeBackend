from django.contrib import admin
from django.contrib.auth.admin import UserAdmin  as BaseUserAdmin
from django.contrib.admin.forms import AdminAuthenticationForm
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import TokenProxy
from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken, EmailAddress

from .models import User

# Unregister allauth social models
try:
    admin.site.unregister(SocialAccount)
    admin.site.unregister(SocialApp)
    admin.site.unregister(SocialToken)
    admin.site.unregister(EmailAddress)
    admin.site.unregister(TokenProxy)
except admin.sites.NotRegistered:
    pass


class EmailAdminAuthenticationForm(AdminAuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Override the label for the username field
        self.fields['username'].label = _('Email')
        # Optional: You can also add a placeholder or help text
        self.fields['username'].widget.attrs.update({'autofocus': True})

admin.site.login_form = EmailAdminAuthenticationForm


# Register your models here.
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('email', 'first_name', 'last_name', 'role')
    search_fields = ('email', 'first_name', 'last_name')
    filter_horizontal = ('groups', 'user_permissions')
