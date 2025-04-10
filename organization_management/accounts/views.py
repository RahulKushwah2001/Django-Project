from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import OrganizationForm, UserRegistrationForm
from .models import CustomUser, Invitation
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404

def home(request):
    return render(request, 'home.html')

def create_organization(request):
    if request.method == 'POST':
        form = OrganizationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Organization created successfully!")
            return redirect('home')
    else:
        form = OrganizationForm()

    return render(request, 'create_organization.html', {'form': form})

def user_registration(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Save the user form data
            form.save()
            messages.success(request, "User successfully registered.")
            return redirect('home')
        else:
            messages.error(request, "There was an error in the form.")
    else:
        form = UserRegistrationForm()

    return render(request, 'user_registration.html', {'form': form})

def user_permissions_view(request):
    # Get the currently logged-in user
    user = request.user

    # Get the permissions directly from the user instance
    permissions = user.user_permissions.all()

    return render(request, 'user_permissions.html', {'permissions': permissions})

def invite_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.is_invited = True
            user.save()

            Invitation.objects.create(user=user, invited_by=request.user)

            messages.success(request, f"User {user.username} invited successfully.")
            return redirect('invitation_list')
        else:
            messages.error(request, "There was an error with the invitation form.")
    else:
        form = UserRegistrationForm()

    return render(request, 'invite_user.html', {'form': form})


def accept_invitation(request):
    user = request.user
    try:
        invitation = Invitation.objects.get(user=user)
        if invitation.accepted:
            return HttpResponse("Already accepted.")
        invitation.accepted = True
        invitation.save()
        return HttpResponse("Invitation accepted. Awaiting admin approval.")
    except Invitation.DoesNotExist:
        return HttpResponse("No invitation found.")

def invitation_list(request):
    invitations = Invitation.objects.all()
    return render(request, 'invitation_list.html', {'invitations': invitations})


@user_passes_test(lambda u: u.is_staff)
@login_required
def approve_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if user.is_invited and not user.is_approved:
        user.is_approved = True
        user.is_active = True
        user.save()
        return HttpResponse(f"User {user.username} approved.")

    return HttpResponse("Invalid action or already approved.")