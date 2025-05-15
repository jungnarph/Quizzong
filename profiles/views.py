from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserForm, ProfileForm
from .models import Profile

@login_required
def profile_view(request):
    return render(request, 'profile/profile.html')

@login_required
def edit_profile_view(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile')
    else:
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    return render(request, 'profile/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

