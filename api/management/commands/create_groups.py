from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from athletes.models import Athlete, Profile
from organizations.models import Organization


class Command(BaseCommand):
    help = 'Create user groups and assign permissions for role-based admin access'

    def add_arguments(self, parser):
        parser.add_argument(
            '--groups',
            type=str,
            default='Athlete,Organization Owner',
            help='Comma-separated list of group names to modify',
        )
        parser.add_argument(
            '--enable-staff',
            action='store_true',
            help='Set is_staff = True for users in the groups',
        )
        parser.add_argument(
            '--disable-staff',
            action='store_true',
            help='Set is_staff = False for users in the groups',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help="Don't save changes; just print what would change",
        )

    def handle(self, *args, **options):
        # Get content types for models
        athlete_ct = ContentType.objects.get_for_model(Athlete)
        profile_ct = ContentType.objects.get_for_model(Profile)
        org_ct = ContentType.objects.get_for_model(Organization)

        # Get or create groups
        athlete_group, athlete_created = Group.objects.get_or_create(name='Athlete')
        org_owner_group, org_created = Group.objects.get_or_create(
            name='Organization Owner'
        )

        # Athlete group permissions: view and change their own profile/athlete records
        athlete_perms = [
            Permission.objects.get(
                content_type=athlete_ct, codename='view_athlete'
            ),
            Permission.objects.get(
                content_type=athlete_ct, codename='change_athlete'
            ),
            Permission.objects.get(
                content_type=profile_ct, codename='view_profile'
            ),
            Permission.objects.get(
                content_type=profile_ct, codename='change_profile'
            ),
        ]

        # Organization Owner group permissions: view/add/change/delete athletes and organization
        org_owner_perms = [
            Permission.objects.get(
                content_type=athlete_ct, codename='view_athlete'
            ),
            Permission.objects.get(
                content_type=athlete_ct, codename='add_athlete'
            ),
            Permission.objects.get(
                content_type=athlete_ct, codename='change_athlete'
            ),
            Permission.objects.get(
                content_type=profile_ct, codename='view_profile'
            ),
            Permission.objects.get(
                content_type=profile_ct, codename='change_profile'
            ),
            Permission.objects.get(
                content_type=org_ct, codename='view_organization'
            ),
            Permission.objects.get(
                content_type=org_ct, codename='change_organization'
            ),
        ]

        # Add permissions to groups
        athlete_group.permissions.set(athlete_perms)
        org_owner_group.permissions.set(org_owner_perms)

        self.stdout.write(
            self.style.SUCCESS(
                'Successfully created groups "Athlete" and "Organization Owner" with appropriate permissions'
            )
        )
        
        # Assign groups to existing users if needed
        args_groups = options.get('groups')
        enable_staff = options.get('enable_staff')
        disable_staff = options.get('disable_staff')
        dry_run = options.get('dry_run')

        if enable_staff and disable_staff:
            self.stdout.write(self.style.ERROR('Cannot specify both --enable-staff and --disable-staff'))
            return

        target_groups = [g.strip() for g in args_groups.split(',') if g.strip()]

        # Helper to process a user
        def process_user(user, group_name):
            if not user.groups.filter(name=group_name).exists():
                user.groups.add(Group.objects.get(name=group_name))
            if enable_staff or disable_staff:
                target = True if enable_staff else False
                if user.is_staff != target:
                    self.stdout.write(f" - {user.username} ({user.email}): is_staff {user.is_staff} -> {target}")
                    if not dry_run:
                        user.is_staff = target
                        user.save()

        # Assign Athlete group to existing athlete users
        if 'Athlete' in target_groups:
            for athlete in Athlete.objects.all():
                if athlete.user:
                    process_user(athlete.user, 'Athlete')

        # Assign Organization Owner group to existing org owners
        if 'Organization Owner' in target_groups:
            for org in Organization.objects.all():
                if org.owner:
                    process_user(org.owner, 'Organization Owner')

        self.stdout.write(self.style.SUCCESS('Group assignments completed for existing users'))
