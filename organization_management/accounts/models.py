from django.db import models
from django.contrib.auth.models import AbstractUser, Permission, Group
import uuid

class Organization(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    industry = models.CharField(max_length=255)
    address = models.TextField()
    contact_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    organization = models.ForeignKey('Organization', on_delete=models.SET_NULL, null=True, blank=True)
    roles = models.ManyToManyField('Role', through='UserRole')  # Many-to-many relationship through UserRole
    is_approved = models.BooleanField(default=False)
    is_invited = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_permissions',  # Custom related name to avoid conflict
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    def __str__(self):
        return self.username

    class Meta:
        permissions = [
            ("can_edit_user", "Can edit user"),
            ("can_view_dashboard", "Can view dashboard"),
        ]


class Role(models.Model):
    SUPER_ADMIN = 'super_admin'
    ADMIN = 'admin'
    BASIC_USER = 'basic_user'

    ROLE_CHOICES = [
        (SUPER_ADMIN, 'Super Admin'),
        (ADMIN, 'Admin'),
        (BASIC_USER, 'Basic User'),
    ]

    name = models.CharField(max_length=255, choices=ROLE_CHOICES)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="roles")
    permissions = models.ManyToManyField(Permission, related_name="roles", blank=True)

    def __str__(self):
        return self.name


class UserRole(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    role = models.ForeignKey('Role', on_delete=models.CASCADE)
    permissions = models.ManyToManyField(Permission)

    def __str__(self):
        return f"{self.user.username} - {self.role.name}"

    def add_default_permissions(self):
        """ Add default permissions to new roles """
        if self.role.name == Role.SUPER_ADMIN:
            self.permissions.add(*Permission.objects.all())  # All permissions for Super Admin
        elif self.role.name == Role.ADMIN:
            # Assign limited permissions for Admin role, for example:
            permissions = Permission.objects.filter(name__in=['view_reports', 'create_tasks'])
            self.permissions.add(*permissions)
        elif self.role.name == Role.BASIC_USER:
            # Basic User has limited permissions
            permissions = Permission.objects.filter(name__in=['view_reports'])
            self.permissions.add(*permissions)


class Designation(models.Model):
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="designations")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="designations")
    permissions = models.ManyToManyField(Permission, related_name="designations", blank=True)

    def __str__(self):
        return self.name

class Invitation(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    accepted = models.BooleanField(default=False)
    invited_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='invitations_sent')
    created_at = models.DateTimeField(auto_now_add=True)