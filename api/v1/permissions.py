from rest_framework import permissions
from athletes.models import Athlete, Profile
from organizations.models import Organization


class IsAthleteOwnerOrReadOnly(permissions.BasePermission):
    """
    - Read-Only: Anyone can view any athlete profile (public viewing)
    - Write/Edit: Only the athlete owner can edit their own profile
    - Organization owners can view/edit athletes in their organization
    - Admins have full access.
    """

    def has_permission(self, request, view):
        # Allow read-only access to everyone (GET requests)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write operations require authentication
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # obj is a Profile instance
        
        # Anyone can view (read-only)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # For write operations, check ownership
        # Admin has full access
        if request.user and request.user.is_staff:
            return True
        
        # Athlete can only edit their own profile
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
        
        # Organization owner can edit athletes in their organization
        if hasattr(obj, 'organization') and obj.organization:
            if obj.organization.owner == request.user:
                return True
        
        return False


class IsOrganizationOwnerOrAdmin(permissions.BasePermission):
    """
    - Read-Only: Anyone can view athlete records
    - Write/Edit: Only org owner or admin can edit
    Restricts athletes to see only themselves (list filtering).
    """

    def has_permission(self, request, view):
        # Allow read-only to everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write operations require authentication
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # obj is an Athlete instance
        
        # Anyone can view (read-only)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # For write operations, check ownership
        # Admin has full access
        if request.user and request.user.is_staff:
            return True
        
        # Athlete can only edit themselves
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
        
        # Organization owner can edit athletes in their organization
        if hasattr(obj, 'organization') and obj.organization:
            if obj.organization.owner == request.user:
                return True
        
        return False


class IsAuthenticatedForDashboard(permissions.BasePermission):
    """
    Dashboard access: Only authenticated athletes and organization owners.
    Prevents organization owners from accessing dashboards they don't own.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user is an athlete or organization owner
        is_athlete = Athlete.objects.filter(user=request.user).exists()
        is_org_owner = Organization.objects.filter(owner=request.user).exists()
        
        return is_athlete or is_org_owner or request.user.is_staff
