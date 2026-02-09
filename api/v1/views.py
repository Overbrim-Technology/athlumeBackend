from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from organizations.models import Organization, School
from athletes.models import Athlete, Profile
from .serializers import OrganizationSerializer, SchoolSerializer, AthleteSerializer, ProfileSerializer
from home.models import FeaturedAthlete, Highlight
from home.serializers import HighlightSerializer
from .permissions import IsAthleteOwnerOrReadOnly, IsOrganizationOwnerOrAdmin, IsAuthenticatedForDashboard

# Create your views here.
# --- Standard CRUD ViewSets ---
class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter queryset based on user role:
        - Organization owners see only their own organization
        - Admins see all organizations
        - Others see all public organizations
        """
        user = self.request.user
        
        # Admin sees all
        if user.is_staff:
            return Organization.objects.all()
        
        # Check if user is an organization owner
        try:
            org = Organization.objects.get(owner=user)
            return Organization.objects.filter(id=org.id)
        except Organization.DoesNotExist:
            # Not an owner - still show all for reference
            return Organization.objects.all()

class SchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer

class AthleteViewSet(viewsets.ModelViewSet):
    queryset = Athlete.objects.all()
    serializer_class = AthleteSerializer
    permission_classes = [IsOrganizationOwnerOrAdmin]

    def get_queryset(self):
        """
        Public viewing: Anyone can see all athletes (read-only)
        Dashboard (authenticated access):
        - Athletes see only themselves
        - Organization owners see athletes in their organization
        - Admins see all
        """
        user = self.request.user
        
        # If user is not authenticated, return all (for public viewing)
        if not user or not user.is_authenticated:
            return Athlete.objects.all()
        
        # For authenticated users, apply filtering based on role
        # Admin sees all athletes
        if user.is_staff:
            return Athlete.objects.all()
        
        # Check if user is an athlete
        try:
            athlete = Athlete.objects.get(user=user)
            # Return only this athlete
            return Athlete.objects.filter(id=athlete.id)
        except Athlete.DoesNotExist:
            pass
        
        # Check if user is an organization owner
        try:
            org = Organization.objects.get(owner=user)
            # Return athletes in this organization
            return Athlete.objects.filter(organization=org)
        except Organization.DoesNotExist:
            pass
        
        # Authenticated user with no role - return empty queryset
        return Athlete.objects.none()

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAthleteOwnerOrReadOnly]

    def get_queryset(self):
        """
        Public viewing: Anyone can see all profiles (read-only based on permission class)
        
        Dashboard (authenticated users):
        - Athletes see only their own profile
        - Organization owners see profiles of athletes in their organization
        - Admins see all profiles
        """
        user = self.request.user
        
        # Public/unauthenticated users see all profiles (permission class enforces read-only)
        if not user.is_authenticated:
            return Profile.objects.all()
        
        # Admin sees all profiles
        if user.is_staff:
            return Profile.objects.all()
        
        # Check if user is an athlete (Profile is multi-table inherit from Athlete)
        try:
            profile = Profile.objects.get(user=user)
            # Return only this profile
            return Profile.objects.filter(id=profile.id)
        except Profile.DoesNotExist:
            pass
        
        # Check if user is an organization owner
        try:
            org = Organization.objects.get(owner=user)
            # Return profiles of athletes in this organization
            return Profile.objects.filter(organization=org)
        except Organization.DoesNotExist:
            pass
        
        # Authenticated user with no role - return empty queryset
        return Profile.objects.none()

# --- The App Home API ---
class AppHomeView(APIView):
    """
    Returns a consolidated JSON payload for the app's home screen.
    Reduces the number of HTTP requests the mobile app needs to make.
    """
    def get(self, request):
        # Query params
        q = request.GET.get('q')  # search query

        # 1. Search (if query provided)
        search_results = None
        if q:
            search_qs = Athlete.objects.filter(
                models.Q(first_name__icontains=q) |
                models.Q(last_name__icontains=q) |
                models.Q(email__icontains=q) |
                models.Q(sport__icontains=q) |
                models.Q(organization__name__icontains=q)
            ).distinct()
            search_results = AthleteSerializer(search_qs, many=True).data

        # 2. Featured athletes chosen by admin (via FeaturedAthlete entries)
        featured_entries = FeaturedAthlete.objects.filter(active=True).select_related('athlete')[:5]
        featured_athletes = [fe.athlete for fe in featured_entries]

        # 3. Other homepage data
        top_schools = School.objects.all()[:3]
        recent_orgs = Organization.objects.exclude(school__isnull=False)[:3]

        # 4. Recent highlights (news) posted by admin
        highlights_qs = Highlight.objects.filter(published=True).order_by('-created_at')[:5]

        # 5. Serialize
        featured_data = AthleteSerializer(featured_athletes, many=True).data
        school_data = SchoolSerializer(top_schools, many=True).data
        org_data = OrganizationSerializer(recent_orgs, many=True).data
        highlights_data = HighlightSerializer(highlights_qs, many=True).data

        payload = {
            "banner_message": "Welcome to the Athlete Portal",
            "featured_athletes": featured_data,
            "top_schools": school_data,
            "partner_organizations": org_data,
            "recent_highlights": highlights_data,
        }

        if search_results is not None:
            payload['search_results'] = search_results

        return Response(payload)
