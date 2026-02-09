from rest_framework import serializers
from organizations.models import Organization, School
from athletes.models import Athlete, Profile, Achievement, Stat, Video


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
    username = serializers.SerializerMethodField()

    def get_username(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    class Meta:
        model = Athlete
        fields = ['id', 'username', 'sport', 'organization', 'organization_name']
        
class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ['id', 'emoji', 'achievement']

class StatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stat
        fields = ['id', 'date', 'event', 'performance', 'highlight']

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'url']

class ProfileSerializer(serializers.ModelSerializer):
    achievements = AchievementSerializer(many=True, read_only=True)
    stats = StatSerializer(many=True, read_only=True)
    videos = VideoSerializer(many=True, read_only=True)

    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model = Profile
        fields = ['id',
                  'first_name',
                  'last_name',
                  'email',
                  'bio',
                  'sport',
                  'school',
                  'graduation_year',
                  'organization_name',
                  'achievements',
                  'stats',
                  'videos',
                  'profile_picture',
                  'banner',
                  'youtube',
                  'facebook',
                  'x',
                  'instagram',]


