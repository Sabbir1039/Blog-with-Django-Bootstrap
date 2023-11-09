from typing import Any
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .models import Profile
from django.views.generic import CreateView, DetailView, UpdateView


class UserRegistrationView(CreateView):
    form_class = UserRegisterForm
    template_name = 'user_accounts/register.html'
    context_object_name = 'form'
    success_url = '/login/'
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = 'Register'
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        profile = Profile(user=self.object)
        profile.save()
        messages.success(self.request, 'Your account was successfully created! Please log in.')
        return response
    
    # Authentication Checks:
    # Depending on app's logic, might want to prevent already
    # authenticated users from accessing the registration page.
    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('/')
        return super().dispatch(*args, **kwargs)


class UserProfileView(DetailView):
    model = Profile
    template_name = 'user_accounts/user_profile.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = 'Profile'
        return context
    
class UserProfileUpdateView(UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'user_accounts/user_profile_update.html'
    
    def get_success_url(self):
        return reverse('profile-detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['profile_form'] = ProfileUpdateForm(instance = self.object.profile)
        return context
    
    def post(self, request, *args, **kwargs):
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile Updated Successfully!')
            return self.form_valid(user_form)
        else:
            return self.form_invalid(user_form, profile_form)