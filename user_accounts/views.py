from typing import Any
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ( 
        UserRegisterForm,
        UserUpdateForm,
        ProfileUpdateForm 
        )
from django.views.generic import (
    CreateView,
    DetailView,
    UpdateView
    )
from django.contrib.auth.views import (
    LoginView,
    LogoutView
    )


class UserRegistrationView(CreateView):
    form_class = UserRegisterForm
    template_name = 'user_accounts/register.html'
    context_object_name = 'form'
    success_url = '/accounts/login/'
    
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
    # dispatch: When a request is made to a Django view, the dispatch() method 
    # is called to handle the incoming request.
    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('/')
        return super().dispatch(*args, **kwargs)


class UserProfileView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'user_accounts/user_profile.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        profile = self.get_object()
        context['title'] = f'Profile-{profile.user}'
        return context
    
    # Ensure that the user can only view their own profile
    def get_object(self, queryset=None):
        return self.request.user.profile
    
class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = UserUpdateForm
    template_name = 'user_accounts/user_profile_update.html'
    
    def get_success_url(self):
        return reverse('profile-detail', kwargs={'pk': self.object.pk})
    
    # Ensure that the user can only view their own profile
    def get_object(self, queryset=None):
        return self.request.user
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        profile = self.request.user.profile #get the user profile
        context['profile_form'] = ProfileUpdateForm(instance = profile)
        context['title'] = f"Update-{self.request.user}'s Profile"
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
            messages.error(request, 'Profile update failed. Please check the form.')
            return self.render_to_response(self.get_context_data(user_form=user_form, profile_form=profile_form))
        
        
class MyLoginView(LoginView):
    redirect_authenticated_user = True
    template_name = 'user_accounts/login.html'
    
    def get_success_url(self):
        return reverse_lazy('home') # set dynamic success url. Higher precedence than success_url
    
    def form_invalid(self, form):
        messages.error(self.request,'Invalid username or password')
        return self.render_to_response(self.get_context_data(form=form))