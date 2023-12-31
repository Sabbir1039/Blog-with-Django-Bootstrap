# urls for user_accounts_app
from django.urls import path
from user_accounts import views as user_accounts_views
from django.contrib.auth import views as auth_views
from .views import UserProfileView, UserProfileUpdateView, MyLoginView

urlpatterns = [
    path('profile/<int:pk>/', UserProfileView.as_view(), name = 'profile-detail'),
    path('profile/<int:pk>/update/', UserProfileUpdateView.as_view(), name = 'user_profile_update'),
    
    path('register/', user_accounts_views.UserRegistrationView.as_view(), name='register'),
    path('login/', MyLoginView.as_view(), name = 'login'),
    path('logout/', auth_views.LogoutView.as_view(template_name="user_accounts/logout.html"), name = 'logout'),
    
     # urls for password reset
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='user_accounts/password_reset.html'),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='user_accounts/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='user_accounts/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='user_accounts/password_reset_complete.html'),
         name='password_reset_complete'),
]

