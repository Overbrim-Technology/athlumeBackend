from django.contrib import admin
from django.contrib.auth.models import Group
from django.shortcuts import redirect
from django.urls import reverse
from .models import Profile, Athlete, Achievement, Stat, Video

# Register your models here.
# @admin.register(Athlete)
# class AthleteAdmin(admin.ModelAdmin):
#     list_display = ('first_name', 'last_name', 'age', 'sport', 'organization')
#     search_fields = ('first_name', 'last_name', 'organization__name') # Search by Org name too!
#     list_filter = ('sport', 'organization')
#     ordering = ('last_name', 'first_name')
    
#     # Optional: Makes the organization dropdown easier to use if you have many orgs
#     autocomplete_fields = ['organization']

class AchievementInline(admin.TabularInline):
    model = Achievement
    extra = 1  # Number of empty rows to show by default
    fields = ('emoji', 'achievement')

class StatInline(admin.TabularInline):
    model = Stat
    extra = 1  # Number of empty rows to show by default
    fields = ('date', 'event', 'performance', 'highlight')

class VideoInline(admin.TabularInline):
    model = Video
    extra = 1  # Number of empty rows to show by default
    fields = ('url',)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    # Use a custom change form template that removes breadcrumbs and object-tools
    change_form_template = 'admin/no_breadcrumb_change_form.html'
    change_list_template = 'admin/no_breadcrumb_change_list.html'
    inlines = [AchievementInline, StatInline, VideoInline]
    list_display = ('first_name', 'last_name', 'organization', 'sport')
    # Don't show user/organization selection to non-superusers; auto-fill instead
    exclude = ('user', 'organization')
    search_fields = ('first_name', 'last_name', 'email')
    actions = None

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # 1. Superusers see everything
        if request.user.is_superuser:
            return qs

        # 2. Organization Owners see only athletes in their organization
        if request.user.groups.filter(name='Organization Owner').exists():
            from organizations.models import Organization
            try:
                org = Organization.objects.get(owner=request.user)
                return qs.filter(organization=org)
            except Organization.DoesNotExist:
                return qs.none()
        
        # 3. Athletes see only their own profile
        if request.user.groups.filter(name='Athlete').exists():
            try:
                athlete = Athlete.objects.get(user=request.user)
                return qs.filter(user=request.user)
            except Athlete.DoesNotExist:
                return qs.none()
        
        # Fallback: See nothing
        return qs.none()

    def get_readonly_fields(self, request, obj=None):
        """
        Prevent Athletes from editing sensitive fields. Organization Owners can edit most fields.
        """
        # If the user is an athlete (and not a superuser), lock these fields
        if request.user.groups.filter(name='Athlete').exists() and not request.user.is_superuser:
            return ['organization', 'user', 'email']
        return []

    def has_module_permission(self, request):
        """Show the app/module in admin for superusers and org owners only.
        Athletes are not shown the module listing but can still access their
        own change page directly if they have permissions.
        """
        if request.user.is_superuser:
            return True
        if request.user.groups.filter(name='Organization Owner').exists():
            return True
        return False

    def has_view_permission(self, request, obj=None):
        # Superusers can view everything
        if request.user.is_superuser:
            return True

        # If no specific object (list view), only org owners may view
        if obj is None:
            return request.user.groups.filter(name='Organization Owner').exists()

        # Athletes can view their own profile
        if request.user.groups.filter(name='Athlete').exists():
            return False # Don't allow athletes to view via admin; they should use the API or a custom frontend.
            # return obj.user == request.user

        # Organization owners can view profiles in their organization
        if request.user.groups.filter(name='Organization Owner').exists():
            return obj.organization is not None and obj.organization.owner == request.user

        return False

    def has_change_permission(self, request, obj=None):
        # Superusers can change everything
        if request.user.is_superuser:
            return True

        # No object provided (list/change list) - prevent athletes from accessing
        if obj is None:
            return request.user.groups.filter(name='Organization Owner').exists()

        # Athletes can change only their own profile
        if request.user.groups.filter(name='Athlete').exists():
            # return False  # Don't allow athletes to change via admin; they should use the API or a custom frontend.
            return obj.user == request.user

        # Organization owners can change profiles belonging to their org
        if request.user.groups.filter(name='Organization Owner').exists():
            return obj.organization is not None and obj.organization.owner == request.user

        return False

    def has_add_permission(self, request):
        """
        Athletes cannot create NEW profiles. Only Org Owners and Superusers can.
        """
        if request.user.groups.filter(name='Athlete').exists():
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        # Athletes should never be allowed to delete via admin
        if request.user.is_superuser:
            return True
        if request.user.groups.filter(name='Athlete').exists():
            return False
        return super().has_delete_permission(request, obj)

    def get_actions(self, request):
        # Remove bulk actions for athletes
        if request.user.groups.filter(name='Athlete').exists():
            return {}
        return super().get_actions(request)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        # If an athlete tries to open someone else's profile, redirect to their own
        if request.user.groups.filter(name='Athlete').exists():
            try:
                my_profile = Profile.objects.get(user=request.user)
                if str(my_profile.pk) != str(object_id):
                    return redirect(reverse('admin:athletes_profile_change', args=[my_profile.pk]))
            except Profile.DoesNotExist:
                # No profile exists yet; let normal permissions handle this
                pass
        return super().change_view(request, object_id, form_url, extra_context)

    # Ensure they can only add achievements to their own profile
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            # Get the user's profile (via the OneToOneField to User)
            try:
                user_profile = Profile.objects.get(user=request.user)
            except Profile.DoesNotExist:
                user_profile = None
            
            if isinstance(instance, Achievement):
                # If they aren't superuser, force the profile to be theirs
                if not request.user.is_superuser and user_profile:
                    instance.profile = user_profile
            elif isinstance(instance, Stat):
                # If they aren't superuser, force the profile to be theirs
                if not request.user.is_superuser and user_profile:
                    instance.profile = user_profile 
            elif isinstance(instance, Video):
                # If they aren't superuser, force the profile to be theirs
                if not request.user.is_superuser and user_profile:
                    instance.profile = user_profile 
            instance.save()
        formset.save_m2m()

    def save_model(self, request, obj, form, change):
        """
        Auto-link the profile to the organization if created by an Org Admin.
        """
        # If the logged-in user is an athlete, ensure the profile links to them
        if request.user.groups.filter(name='Athlete').exists() and not request.user.is_superuser:
            obj.user = request.user

        # If the logged-in user is an organization owner, link the profile to their org
        if request.user.groups.filter(name='Organization Owner').exists() and not request.user.is_superuser:
            try:
                from organizations.models import Organization
                org = Organization.objects.get(owner=request.user)
                obj.organization = org
            except Organization.DoesNotExist:
                pass

        super().save_model(request, obj, form, change)

        # Ensure a corresponding Athlete parent row exists for this Profile
        try:
            from .models import Athlete as AthleteModel
            if not AthleteModel.objects.filter(pk=obj.pk).exists():
                AthleteModel.objects.create(
                    pk=obj.pk,
                    first_name=obj.first_name,
                    last_name=obj.last_name,
                    phone=getattr(obj, 'phone', ''),
                    email=getattr(obj, 'email', ''),
                    age=getattr(obj, 'age', None),
                    bio=getattr(obj, 'bio', ''),
                    sport=getattr(obj, 'sport', ''),
                    school=getattr(obj, 'school', ''),
                    graduation_year=getattr(obj, 'graduation_year', None),
                    coach_name=getattr(obj, 'coach_name', ''),
                    organization=getattr(obj, 'organization', None),
                    user=getattr(obj, 'user', None),
                )
        except Exception:
            # If anything goes wrong, don't block admin save
            pass

@admin.register(Athlete)
class AthleteAdmin(admin.ModelAdmin):
    # Use a custom change form template that removes breadcrumbs and object-tools
    change_form_template = 'admin/no_breadcrumb_change_form.html'
    change_list_template = 'admin/no_breadcrumb_change_list.html'
    list_display = ('first_name', 'last_name', 'organization', 'sport')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('sport', 'organization')
    ordering = ('last_name', 'first_name')
    autocomplete_fields = ['organization']

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
            return ['organization', 'sport']
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

    def has_module_permission(self, request):
        # Hide the Athlete model from the admin index for non-superusers
        return request.user.is_superuser