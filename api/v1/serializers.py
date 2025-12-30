from rest_framework import serializers
from organizations.models import Organization, School
from athletes.models import Athlete


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'

class SchoolSerializer(serializers.ModelSerializer):
    # This will include inherited fields (name, logo) automatically
    class Meta:
        model = School
        fields = '__all__'

class AthleteSerializer(serializers.ModelSerializer):
    # Optional: Display the organization name instead of just ID
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model = Athlete
        fields = ['id', 'first_name', 'last_name', 'sport', 'organization', 'organization_name']