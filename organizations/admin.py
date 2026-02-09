from django.contrib import admin
from django.contrib.auth.models import Group
from .models import Organization, School
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages

# Register your models here.
# @admin.register(Organization)
# class OrganizationAdmin(admin.ModelAdmin):
#     list_display = ('name', 'created_at', 'id')
#     search_fields = ('name',)
#     list_filter = ('created_at',)
#     ordering = ('-created_at',)

# @admin.register(School)
# class SchoolAdmin(admin.ModelAdmin):
#     # School inherits fields from Organization, so we can display them here
#     list_display = ('name', 'state', 'city', 'created_at')
#     search_fields = ('name', 'state', 'city')
#     list_filter = ('state',)

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    # Use custom templates that remove the breadcrumb rail
    change_form_template = 'admin/no_breadcrumb_change_form.html'
    change_list_template = 'admin/no_breadcrumb_change_list.html'
    list_display = ('name', 'created_at')
    search_fields = ('name', 'email', 'state', 'city')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # 1. Superusers see all organizations
        if request.user.is_superuser:
            return qs
        
        # 2. Organization Owners see ONLY their own organization
        if request.user.groups.filter(name='Organization Owner').exists():
            return qs.filter(owner=request.user)
            
        # 3. Everyone else (e.g. Athletes) sees nothing
        return qs.none()

    def has_add_permission(self, request):
        # Only Superusers can create new organizations
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        # Only Superusers can delete organizations
        return request.user.is_superuser

    def has_module_permission(self, request):
        """Hide the organizations app/module from non-superusers in the admin index.
        Organization owners will not see the Organizations app listing, but can
        still access their specific organization change page directly if they
        have the proper object-level permission.
        """
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        # Superusers can view everything
        if request.user.is_superuser:
            return True

        # If no specific object (list view), do not allow org owners to see the module
        if obj is None:
            return False

        # Allow org owners to view their own organization
        if request.user.groups.filter(name='Organization Owner').exists():
            return obj.owner == request.user

        return False

    def has_change_permission(self, request, obj=None):
        # Superusers can change everything
        if request.user.is_superuser:
            return True

        # Prevent access to the change list
        if obj is None:
            return False

        # Organization owners can change only their own organization
        if request.user.groups.filter(name='Organization Owner').exists():
            return obj.owner == request.user

        return False

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('my-org/', self.admin_site.admin_view(self.my_org_view), name='organizations_organization_my_org'),
        ]
        return custom_urls + urls

    def my_org_view(self, request):
        try:
            org = Organization.objects.get(owner=request.user)
            return redirect(f'/admin/organizations/organization/{org.pk}/change/')
        except Organization.DoesNotExist:
            messages.error(request, "You do not have an associated organization.")
            return redirect('admin:index')

@admin.register(School)
class SchoolAdmin(OrganizationAdmin):
    # Inherits the protection logic from OrganizationAdmin above
    list_display = ('name', 'state', 'city')