from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer
from rest_framework import serializers
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class CustomRegisterSerializer(RegisterSerializer):
    """
    Extended registration serializer that creates an Athlete or Organization
    record automatically based on the 'role' field.
    """
    
    ROLE_CHOICES = [
        ('athlete', 'Athlete'),
        ('organization', 'Organization/School Manager'),
    ]
    
    # Override username to make it not required (will be set to email automatically)
    username = None
    
    role = serializers.ChoiceField(
        choices=ROLE_CHOICES,
        required=True,
        help_text="Select 'athlete' to register as an athlete, or 'organization' to manage a school/organization."
    )
    
    # Core fields required at onboarding
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=30)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=30)
    phone = serializers.CharField(required=False, allow_blank=False, max_length=15)
    
    # Organization-specific fields
    org_name = serializers.CharField(required=False, allow_blank=True, max_length=100)
    
    # Athlete-specific fields
    sport = serializers.CharField(required=False, allow_blank=True, max_length=250)
    school = serializers.CharField(required=False, allow_blank=True, max_length=50)
    
    def save(self, request):
        """
        Override the save method to create appropriate role record and assign to group.
        """
        # Lazy import to avoid circular imports during migrations
        from athletes.models import Profile
        from organizations.models import Organization
        from django.contrib.auth.models import Group
        
        # Call parent save to create the User object
        user = super().save(request)
        
        # Set username to email for easier authentication
        user.username = user.email
        user.save()
        
        # Get the role from the validated data
        role = self.validated_data.get('role')
        
        # Extract common fields
        first_name = self.validated_data.get('first_name', '')
        last_name = self.validated_data.get('last_name', '')
        phone = self.validated_data.get('phone', '')
        email = user.email

        # keep User model first/last in sync
        try:
            user.first_name = first_name
            user.last_name = last_name
            user.save()
        except Exception:
            # If user model does not accept these fields, ignore
            pass
        
        # Create the appropriate record based on role
        if role == 'athlete':
            # Create Profile (which inherits from Athlete) with only supplied fields
            profile_data = {
                'user': user,
                'first_name': first_name,
                'last_name': last_name,
                'phone': phone,
                'email': email,
            }
            # Optional athlete fields
            if 'sport' in self.validated_data:
                profile_data['sport'] = self.validated_data.get('sport')
            if 'school' in self.validated_data:
                profile_data['school'] = self.validated_data.get('school')

            Profile.objects.create(**profile_data)
        
        elif role == 'organization':
            org_name = self.validated_data.get('org_name') or user.username
            org_data = {
                'owner': user,
                'name': org_name,
                'email': email,
            }
            # include phone if provided
            if phone:
                org_data['phone'] = phone
            # optional address/state/city can be filled later
            Organization.objects.create(**org_data)
        
        # Assign user to appropriate group (do NOT make them staff)
        if role == 'athlete':
            athlete_group = Group.objects.get(name='Athlete')
            user.groups.add(athlete_group)
            user.save()
        elif role == 'organization':
            org_owner_group = Group.objects.get(name='Organization Owner')
            user.groups.add(org_owner_group)
            user.save()
        
        return user

class CustomLoginSerializer(LoginSerializer):
    """
    Custom login serializer that accepts email and password instead of username.
    Since username is set to email during registration, we can authenticate with email directly.
    """
    username = None  # Remove the username field
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
        required=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            msg = _('Must include "email" and "password".')
            raise ValidationError(msg, code='required_fields')
        
        # Authenticate using email (which is also the username)
        user = authenticate(request=self.context.get('request'), username=email, password=password)
        
        if not user:
            msg = _('Unable to log in with provided credentials.')
            raise ValidationError(msg, code='authorization')
        
        attrs['user'] = user
        return attrs