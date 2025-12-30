from django.contrib import admin
from .models import Organization, School

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
    list_display = ('name', 'created_at')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # 1. Superusers see all organizations
        if request.user.is_superuser:
            return qs
        
        # 2. Org Admins see ONLY their own organization
        if hasattr(request.user, 'organization'):
            return qs.filter(id=request.user.organization.id)
            
        # 3. Everyone else (e.g. Athletes) sees nothing
        return qs.none()

    def has_add_permission(self, request):
        # Prevent Schools from creating NEW Schools (only Superuser does that)
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        # Prevent Schools from deleting themselves
        return request.user.is_superuser

@admin.register(School)
class SchoolAdmin(OrganizationAdmin):
    # Inherits the protection logic from OrganizationAdmin above
    list_display = ('name', 'state', 'city')