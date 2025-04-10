from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create-organization/', views.create_organization, name='create_organization'),
    path('register/', views.user_registration, name='user_registration'),
    path('user-permissions/', views.user_permissions_view, name='user_permissions'),
    path('invite/', views.invite_user, name='invite_user'),
    path('invitations/', views.invitation_list, name='invitation_list'),
    path('approve/<int:user_id>/', views.approve_user, name='approve_user'),
    #path('user/<int:user_id>/permissions/', views.user_permissions, name='user_permissions'),
    #path('assign-role/<int:user_id>/<int:role_id>/', views.assign_role_to_user, name='assign_role_to_user'),
]
