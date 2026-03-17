from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from organizations.models import Organization, School
from athletes.models import Athlete, Profile, Achievement, Stat, Video
from .serializers import (OrganizationSerializer, SchoolSerializer, AthleteSerializer, 
                          ProfileSerializer, AchievementSerializer, StatSerializer, VideoSerializer)
from home.models import FeaturedAthlete, Highlight
from home.serializers import HighlightSerializer
from .permissions import IsAthleteOwnerOrReadOnly, IsOrganizationOwnerOrAdmin, IsAuthenticatedForDashboard, IsProfileOwner

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
    permission_classes = [AllowAny]

    def get(self, request):
        # 1. Optimized Featured Athletes
        # We follow the relationship from FeaturedAthlete -> Athlete -> User/Organization
        featured_entries = FeaturedAthlete.objects.filter(active=True).select_related(
            'athlete__user',          # To get first/last name
            'athlete__organization'   # To get the school/org name
        )[:5]
        featured_athletes = [fe.athlete for fe in featured_entries]

        # 2. Schools (Usually simple, but order_by is good)
        top_schools = School.objects.all().order_by('name')[:3]

        # 3. Organizations
        recent_orgs = Organization.objects.exclude(school__isnull=False).select_related(
            'owner'  # If the serializer shows owner info
        ).order_by('-id')[:3]

        # 4. Highlights (Crucial optimization)
        # Highlights almost always show the Athlete's name or photo
        highlights_qs = Highlight.objects.filter(published=True).select_related(
            'created_by'
        ).order_by('-created_at')[:5]

        # --- SERIALIZATION ---
        payload = {
            "banner_message": "Welcome to the Athlete Portal",
            "featured_athletes": ProfileSerializer(featured_athletes, many=True, context={"request": request}).data,
            "top_schools": SchoolSerializer(top_schools, many=True, context={"request": request}).data,
            "partner_organizations": OrganizationSerializer(recent_orgs, many=True, context={"request": request}).data,
            "recent_highlights": HighlightSerializer(highlights_qs, many=True, context={"request": request}).data,
        }

        return Response(payload)


class GlobalSearchView(APIView):
    permission_classes = [AllowAny] # Public search

    def get(self, request):
        q = request.GET.get('q', '').strip()
        if not q or len(q) < 2:
            return Response([])

        # We use select_related to grab the User and Organization 
        # so the Serializer doesn't have to hit the DB again.
        results = Profile.objects.select_related(
            'user', 
            'organization'
        ).prefetch_related('user__groups').filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(email__icontains=q) |
            Q(sport__icontains=q) |
            Q(organization__name__icontains=q)
        ).distinct()[:20]

        return Response(ProfileSerializer(results, many=True).data)


# --- Achievement, Stat, and Video ViewSets ---
class AchievementViewSet(viewsets.ModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
    permission_classes = [IsProfileOwner]

    def get_queryset(self):
        """
        Filter achievements based on profile ownership.
        - Public: Anyone can view all achievements (read-only)
        - Authenticated: Athletes can only see their own achievements for editing
        """
        user = self.request.user
        
        # For read-only requests, return all achievements
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return Achievement.objects.all()
        
        # For write operations, filter to only this athlete's achievements
        if user and user.is_authenticated:
            try:
                profile = Profile.objects.get(user=user)
                return Achievement.objects.filter(profile=profile)
            except Profile.DoesNotExist:
                pass
        
        # Admin sees all
        if user and user.is_staff:
            return Achievement.objects.all()
        
        return Achievement.objects.none()

    def perform_create(self, serializer):
        """Automatically associate the achievement with the authenticated user's profile"""
        try:
            profile = Profile.objects.get(user=self.request.user)
            serializer.save(profile=profile)
        except Profile.DoesNotExist:
            raise ValidationError("User does not have a Profile. Please create one first.")


class StatViewSet(viewsets.ModelViewSet):
    queryset = Stat.objects.all()
    serializer_class = StatSerializer
    permission_classes = [IsProfileOwner]

    def get_queryset(self):
        """
        Filter stats based on profile ownership.
        - Public: Anyone can view all stats (read-only)
        - Authenticated: Athletes can only see their own stats for editing
        """
        user = self.request.user
        
        # For read-only requests, return all stats
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return Stat.objects.all()
        
        # For write operations, filter to only this athlete's stats
        if user and user.is_authenticated:
            try:
                profile = Profile.objects.get(user=user)
                return Stat.objects.filter(profile=profile)
            except Profile.DoesNotExist:
                pass
        
        # Admin sees all
        if user and user.is_staff:
            return Stat.objects.all()
        
        return Stat.objects.none()

    def perform_create(self, serializer):
        """Automatically associate the stat with the authenticated user's profile"""
        try:
            profile = Profile.objects.get(user=self.request.user)
            serializer.save(profile=profile)
        except Profile.DoesNotExist:
            raise ValidationError("User does not have a Profile. Please create one first.")


class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsProfileOwner]

    def get_queryset(self):
        """
        Filter videos based on profile ownership.
        - Public: Anyone can view all videos (read-only)
        - Authenticated: Athletes can only see their own videos for editing
        """
        user = self.request.user
        
        # For read-only requests, return all videos
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return Video.objects.all()
        
        # For write operations, filter to only this athlete's videos
        if user and user.is_authenticated:
            try:
                profile = Profile.objects.get(user=user)
                return Video.objects.filter(profile=profile)
            except Profile.DoesNotExist:
                pass
        
        # Admin sees all
        if user and user.is_staff:
            return Video.objects.all()
        
        return Video.objects.none()

    def perform_create(self, serializer):
        """Automatically associate the video with the authenticated user's profile"""
        try:
            profile = Profile.objects.get(user=self.request.user)
            serializer.save(profile=profile)
        except Profile.DoesNotExist:
            raise ValidationError("User does not have a Profile. Please create one first.")
