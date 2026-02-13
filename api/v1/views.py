from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Q
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
    permission_classes = [IsOrganizationOwnerOrAdmin]

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

        # Admin sees all athletes
        if user.is_staff:
            return Athlete.objects.all()
        
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
        
        # Check if user is an organization owner
        try:
            org = Organization.objects.get(owner=user)
            # Return profiles of athletes in this organization
            return Profile.objects.filter(organization=org)
        except Organization.DoesNotExist:
            pass

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
        
        # Authenticated user with no role - return empty queryset
        return Profile.objects.none()

# --- The App Home API ---
class AppHomeView(APIView):
    """
    Public Home Screen Endpoint.
    Returns a consolidated JSON payload for the app's home screen.
    Reduces the number of HTTP requests the mobile app needs to make.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        # HOME DATA LOGIC ---
        featured_entries = FeaturedAthlete.objects.filter(active=True).select_related('athlete')[:5]
        featured_athletes = [fe.athlete for fe in featured_entries]

        # Top Schools: Order by name or ID to prevent "shuffling" on refresh
        top_schools = School.objects.all().order_by('name')[:3]

        # Recent Orgs: explicitly order by creation date
        recent_orgs = Organization.objects.exclude(school__isnull=False)\
                                          .order_by('-id')[:3]

        # Highlights: already ordered correctly in your code
        highlights_qs = Highlight.objects.filter(published=True).order_by('-created_at')[:5]

        # --- 3. SERIALIZATION ---
        payload = {
            "banner_message": "Welcome to the Athlete Portal",
            "featured_athletes": ProfileSerializer(featured_athletes, many=True).data,
            "top_schools": SchoolSerializer(top_schools, many=True).data,
            "partner_organizations": OrganizationSerializer(recent_orgs, many=True).data,
            "recent_highlights": HighlightSerializer(highlights_qs, many=True).data,
        }

        return Response(payload)


class GlobalSearchView(APIView):
    permission_classes = [AllowAny] # Public search

    def get(self, request):
        q = request.GET.get('q', '').strip()
        
        # If empty search, return empty list immediately
        if not q or len(q) < 2:
            return Response([])

        # Perform the search
        search_qs = Profile.objects.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(email__icontains=q) |
            Q(sport__icontains=q) |
            Q(organization__name__icontains=q)
        ).distinct()

        # LIMIT TO 20 RESULTS
        # This makes the response lightning fast
        results = search_qs[:20]

        return Response(ProfileSerializer(results, many=True).data)