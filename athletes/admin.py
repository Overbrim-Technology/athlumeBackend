from django.contrib import admin
from .models import Athlete

# Register your models here.
# @admin.register(Athlete)
# class AthleteAdmin(admin.ModelAdmin):
#     list_display = ('first_name', 'last_name', 'age', 'sport', 'organization')
#     search_fields = ('first_name', 'last_name', 'organization__name') # Search by Org name too!
#     list_filter = ('sport', 'organization')
#     ordering = ('last_name', 'first_name')
    
#     # Optional: Makes the organization dropdown easier to use if you have many orgs
#     autocomplete_fields = ['organization']
@admin.register(Athlete)
class AthleteAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'organization', 'sport')
    
    def get_queryset(self, request):
        """
        Filter the list of athletes based on the logged-in user.
        """
        qs = super().get_queryset(request)
        
        # 1. Superusers see everything
        if request.user.is_superuser:
            return qs
        
        # 2. Organization/School Admins see only their own athletes
        # We check if the user 'owns' an organization
        if hasattr(request.user, 'organization'):
            return qs.filter(organization=request.user.organization)
            
        # 3. Athletes see only themselves
        if hasattr(request.user, 'athlete'):
            return qs.filter(user=request.user)
            
        # Fallback: See nothing
        return qs.none()

    def get_readonly_fields(self, request, obj=None):
        """
        Prevent Athletes from editing sensitive fields (like their Organization).
        """
        if not request.user.is_superuser and hasattr(request.user, 'athlete'):
            return ['organization', 'sport'] # Lock these fields for athletes
        return []

    def save_model(self, request, obj, form, change):
        """
        When an Organization creates an athlete, automatically link it 
        to that Organization.
        """
        # If the user is an Org Admin and creating a new athlete
        if not request.user.is_superuser and hasattr(request.user, 'organization'):
            obj.organization = request.user.organization
        
        super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        """
        Athletes cannot create NEW athlete profiles. 
        Only Orgs and Superusers can.
        """
        if hasattr(request.user, 'athlete'):
            return False
        return True