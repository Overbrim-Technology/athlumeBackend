from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from organizations.models import Organization, School
from athletes.models import Athlete
from .serializers import OrganizationSerializer, SchoolSerializer, AthleteSerializer

# Create your views here.
# --- Standard CRUD ViewSets ---
class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

class SchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer

class AthleteViewSet(viewsets.ModelViewSet):
    queryset = Athlete.objects.all()
    serializer_class = AthleteSerializer

# --- The App Home API ---
class AppHomeView(APIView):
    """
    Returns a consolidated JSON payload for the app's home screen.
    Reduces the number of HTTP requests the mobile app needs to make.
    """
    def get(self, request):
        # 1. Fetch Featured Data (You can add filters here, e.g., 'top 5')
        featured_athletes = Athlete.objects.all()[:5]
        top_schools = School.objects.all()[:3]
        recent_orgs = Organization.objects.exclude(school__isnull=False)[:3] # Exclude schools to show just generic orgs

        # 2. Serialize the data
        athlete_data = AthleteSerializer(featured_athletes, many=True).data
        school_data = SchoolSerializer(top_schools, many=True).data
        org_data = OrganizationSerializer(recent_orgs, many=True).data

        # 3. Return consolidated response
        return Response({
            "banner_message": "Welcome to the Athlete Portal",
            "featured_athletes": athlete_data,
            "top_schools": school_data,
            "partner_organizations": org_data
        })
