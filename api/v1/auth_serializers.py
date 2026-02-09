from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from django.conf import settings


class CustomRegisterSerializer(RegisterSerializer):
    """
    Extended registration serializer that creates an Athlete or Organization
    record automatically based on the 'role' field.
    """
    
    ROLE_CHOICES = [
        ('athlete', 'Athlete'),
        ('organization', 'Organization/School Manager'),
    ]
    
    role = serializers.ChoiceField(
        choices=ROLE_CHOICES,
        required=True,
        help_text="Select 'athlete' to register as an athlete, or 'organization' to manage a school/organization."
    )
    
    # Optional: Accept additional athlete/org info during registration
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=30)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=30)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=15)
    
    # Organization-specific fields
    org_name = serializers.CharField(required=False, allow_blank=True, max_length=100)
    
    # Athlete-specific fields
    sport = serializers.CharField(required=False, allow_blank=True, max_length=250)
    school = serializers.CharField(required=False, allow_blank=True, max_length=50)
    
    def save(self, request):
        """
        Override the save method to create appropriate role record.
        """
        # Lazy import to avoid circular imports during migrations
        from athletes.models import Athlete
        from organizations.models import Organization
        
        # Call parent save to create the User object
        user = super().save(request)
        
        # Get the role from the validated data
        role = self.validated_data.get('role')
        
        # Extract common fields
        first_name = self.validated_data.get('first_name', '')
        last_name = self.validated_data.get('last_name', '')
        phone = self.validated_data.get('phone', '')
        email = user.email
        
        # Create the appropriate record based on role
        if role == 'athlete':
            Athlete.objects.create(
                user=user,
                first_name=first_name or user.username[:15],
                last_name=last_name or '',
                phone=phone or '000-000-0000',
                email=email,
                age=18,  # Default value - can be updated later
                bio='',
                sport=self.validated_data.get('sport', 'Unknown'),
                school=self.validated_data.get('school', 'Unknown'),
                graduation_year=2025,  # Default - can be updated later
                coach_name='',
                organization=None,
            )
        
        elif role == 'organization':
            Organization.objects.create(
                owner=user,
                name=self.validated_data.get('org_name', user.username),
                address='',
                phone=phone or '000-000-0000',
                email=email,
                state='',
                city='',
            )
        
        return user
