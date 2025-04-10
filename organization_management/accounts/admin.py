from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponse
from django.urls import path
from django.utils.html import format_html
from .models import Organization, CustomUser, Role, UserRole, Permission, Designation
from django.contrib.admin.views.decorators import staff_member_required

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'industry', 'contact_email', 'created_at')

def approve_selected_users(modeladmin, request, queryset):
    queryset.update(is_approved=True, is_active=True)
    modeladmin.message_user(request, "Selected users have been approved.")

approve_selected_users.short_description = "Approve selected users"

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'mobile', 'get_permissions', 'approve_link']
    search_fields = ['username', 'email']
    list_filter = ['is_active', 'is_staff']
    actions = [approve_selected_users]  # Now it works without the NameError

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'mobile', 'organization')}),
        ('Invite & Approval', {'fields': ('is_invited', 'is_approved')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1', 'password2', 'organization', 'mobile', 'is_invited', 'is_approved',
                'is_active', 'is_staff')
        }),
    )

    filter_horizontal = ('groups', 'user_permissions')

    def get_permissions(self, obj):
        """ Returns a comma-separated list of the permissions assigned to the user """
        permissions = obj.user_permissions.all()
        return ", ".join([perm.name for perm in permissions])

    def approve_link(self, obj):
        """ Display a link to approve a user directly from the admin list """
        if obj.is_invited and not obj.is_approved:
            return format_html(
                '<a href="{}" class="button">Approve</a>',
                f"/admin/approve/{obj.id}/"
            )
        return "Already Approved"

    approve_link.short_description = "Approval Link"


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'get_permissions')
    search_fields = ('name',)

    def get_permissions(self, obj):
        """ Display permissions related to the role """
        return ", ".join([perm.name for perm in obj.permissions.all()])
    get_permissions.short_description = 'Permissions'

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'codename', 'content_type')
    search_fields = ['name', 'codename']

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'get_permissions')
    search_fields = ('user__username', 'role__name')

    def get_permissions(self, obj):
        """ Display permissions related to the user-role """
        return ", ".join([perm.name for perm in obj.permissions.all()])
    get_permissions.short_description = 'Permissions'

    filter_horizontal = ('permissions',)

# Register the Designation model in the admin panel
@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'role')
    search_fields = ('name', 'organization__name', 'role__name')


@staff_member_required
def approve_user(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    if user.is_invited and not user.is_approved:
        user.is_approved = True
        user.is_active = True  # Now they can log in
        user.save()
        return HttpResponse(f"User {user.username} approved successfully.")
    return HttpResponse("Invalid action.")
