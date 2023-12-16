# Full Featured Blog Web App with Django+Bootstrap

Welcome to the full featured django blog web app, a versatile web application that provides a robust blogging platform with user registration, authentication, and profile management features. This project is built using the Django web framework and Bootstrap, making it scalable, secure, and customizable for various blogging needs.

## Introduction

This Django project combines two essential components:

- **Blog App:** Allows users to create, edit, and delete blog posts, categorize them, leave comments, and like posts.
- **User Accounts App:** Provides user registration, authentication, reset user password with email and profile management functionalities, including the option to upload profile pictures.

## Project Structure

The project follows a modular structure to enhance maintainability and organization. Below is a sample project structure to help you navigate the codebase effectively:

```plaintext
django_blog_and_user_accounts/
|-- blog_app/
|   |-- migrations/
|   |-- static/
|   |-- templates/
|   |-- __init__.py
|   |-- admin.py
|   |-- apps.py
|   |-- forms.py
|   |-- models.py
|   |-- tests.py
|   |-- urls.py
|   `-- views.py
|-- user_accounts/
|   |-- migrations/
|   |-- static/
|   |-- templates/
|   |-- __init__.py
|   |-- admin.py
|   |-- apps.py
|   |-- forms.py
|   |-- models.py
|   |-- tests.py
|   |-- urls.py
|   `-- views.py
|-- manage.py
|-- django_blog_project/
|   |-- __init__.py
|   |-- settings.py
|   |-- urls.py
|   `-- wsgi.py
|-- media/
|-- requirements.txt
|-- README.md
```
## Django Blog App Explanation (*with codes*)

## Overview

This Django app provides a simple blog system with features like post creation, category management, user authentication, comments, and post likes.

## Table of Contents

- [Models](#models)
- [Views](#views)
- [URLs](#urls)

## Models

### Imports

```python
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from PIL import Image
from django.urls import reverse
```

### Category Model

The `Category` model represents a blog category with a name and an optional description.

```python
# models.py
class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
```

### Post Model

The `Post` model represents a blog post with a title, content, creation and update timestamps, author, categories, publication status, and a cover image.

```python
# models.py
class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    categories = models.ManyToManyField(Category, related_name='posts')
    is_published = models.BooleanField(default=True)
    cover_image = models.ImageField(default='cover.jpg', upload_to='cover_pics')
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})
    
    # resize image before saveing
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            img = Image.open(self.cover_image.path)
            # Set a maximum size for the profile picture
            max_size = (1080, 620)
            if img.height > max_size[1] or img.width > max_size[0]:
                img.thumbnail(max_size)
                img.save(self.cover_image.path)
        except Exception as e:
            print("Error occured while resizing image!", e)
```

### Comment Model

The `Comment` model represents a user comment on a blog post.

```python
# models.py
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {str(self.author)} on {str(self.post)}"
```

### Like Model

The `Like` model represents a user's like on a blog post.

```python
# models.py
class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        # Ensure each user can only like a post once.
        unique_together = ('post', 'user')  

    def __str__(self):
        return f"Like by {self.user} on {self.post}"
```

## Views

The app contains various views, including the home page, post list, post creation, post detail, post update, post delete, and an about page.

```python
from typing import Any
from django.db.models.query import QuerySet
from django.db import models
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.http import Http404
from urllib.parse import urlparse, parse_qs
from django.core.exceptions import ObjectDoesNotExist

from .models import (
    Post,
    Like,
    Category,
    Comment
    )

from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
    )

from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    UpdateView,
    DeleteView,
    TemplateView,
    )

import logging

logger = logging.getLogger(__name__)


# views here.
class HomePageView(ListView):
    model = Post
    template_name = 'blog_app/home.html'
    context_object_name = 'posts'
     
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]: # key: string type & value: any type
        context = super().get_context_data(**kwargs)
        try:
            context['title'] = 'Blog Home'
            context['recent_posts'] = Post.objects.all().order_by('-created_at')[:5]
            most_liked_posts = Post.objects.annotate(like_count=models.Count('likes')).order_by('-like_count')[:3]
            context['featured_posts'] = most_liked_posts
            context['categories'] = Category.objects.all()
            return context
        except (Post.DoesNotExist, Category.DoesNotExist) as e:
            # Handle the specific exceptions expect to encounter
            logger.error(f"Error retrieving data for HomePageView: {e}")
            context['error_message'] = "An error occurred while retrieving data."
        except Http404 as e:
            # Handle Http404 exception
            logger.warning(f"Page not found in HomePageView: {e}")
            raise e  # Re-raise Http404 to allow Django to handle it
        except Exception as e:
            # Handle any unexpected exceptions
            logger.exception(f"Uncaught exception in HomePageView: {e}")
            context['error_message'] = "An unexpected error occurred while processing your request."

        return context
    
class PostListView(ListView):
    model = Post
    context_object_name = "posts"
    paginate_by = 3
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        try:
            context['title'] = "All Posts"
            context['categories'] = Category.objects.all()
            
            # Parse the URL and extract the 'category' and search parameter
            parsed_url = urlparse(self.request.get_full_path())
            query_params = parse_qs(parsed_url.query)
            category_id = query_params.get('category', [None])[0]
            search_str = query_params.get('search', [None])[0]
            # Add the selected category and search str to the context
            context['selected_category'] = int(category_id) if category_id is not None else None # [hint]initially this is string not int
            context['searched_text'] = str(search_str) if search_str is not None else None # [hint] this is string
            return context
        
        except (Category.DoesNotExist) as e:
            # Handle the specific exceptions expect to encounter
            logger.error(f"Error retrieving category data for PostListView: {e}")
            context['error_message'] = "An error occurred while retrieving data."
            raise e  # Re-raise the exception to stop further execution
            
        except Http404 as e:
            # Handle Http404 exception
            logger.warning(f"Page not found in PostListView: {e}")
            raise e  # Re-raise Http404 to allow Django to handle it
        
        except Exception as e:
            # Handle any unexpected exceptions
            logger.exception(f"Uncaught exception in PostListView: {e}")
            context['error_message'] = "An unexpected error occurred while processing your request."
        return context
    
    def get_queryset(self) -> QuerySet[Any]:
        queryset = super().get_queryset()
        category_id = self.request.GET.get('category')
        search_query = self.request.GET.get('search')

        try:
            # Apply category filter
            if category_id:
                queryset = queryset.filter(categories__id=category_id)

            # Apply search filter
            if search_query:
                queryset = queryset.filter(title__icontains=search_query)

            return queryset

        except ObjectDoesNotExist as e:
            # Handle the specific exceptions expect to encounter
            logger.error(f"Error retrieving queryset data for PostListView: {e}")
            # may want to set an error message in the context here if needed
            raise e  # Re-raise the exception to stop further execution

        except Exception as e:
            # Handle any unexpected exceptions
            logger.exception(f"Uncaught exception in PostListView: {e}")
            # may want to set an error message in the context here if needed
            raise e  # Re-raise the exception to stop further execution
            

class PostCreateView(LoginRequiredMixin,CreateView):
    model = Post
    fields = ['title', 'content', 'categories', 'is_published', 'cover_image']
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['header'] = 'Create New Post'
        context['title'] = 'New Post'
        return context
    
    def form_valid(self, form: BaseModelForm) -> HttpResponse: 
        form.instance.author = self.request.user
        return super().form_valid(form)   
    

class PostDetailView(DetailView):
    model = Post
    context_object_name = 'post'
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        post = context['post']
        # Check if the user is authenticated before checking likes
        context['is_liked'] = post.likes.filter(user=self.request.user).exists() if self.request.user.is_authenticated else False
        context['title'] = f'Post-{post.title}'
        return context
    
    def post(self, request, *args, **kwargs):
        # Handling comment submission
        if 'comment_content' in self.request.POST:
            if self.request.user.is_authenticated:
                post = self.get_object()
                comment_content = self.request.POST['comment_content']
                Comment.objects.create(post=post, author=request.user, content=comment_content)
                messages.success(request, 'Comment added successfully.')
                return redirect('post-detail', pk=post.pk)
            else:
                messages.warning(request, 'Can not comment on this post! You need to login first.')
                return redirect('login')

        # Handling like button click
        if 'like_button' in self.request.POST:
            if self.request.user.is_authenticated:
                post = self.get_object()
                # Check if the user already liked the post
                if not Like.objects.filter(post=post, user=request.user).exists():
                    Like.objects.create(post=post, user=request.user)
                    messages.success(request, 'Liked the post!')
                else:
                    messages.warning(request, 'You have already liked this post.')
                return redirect('post-detail', pk=post.pk)
            else:
                 messages.warning(request, 'Can not like the post! You need to login first.')
                 return redirect('login')

        return super().post(request, *args, **kwargs)
    
    
class PostUpdateView(UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content', 'categories', 'is_published', 'cover_image']
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['header'] = f'Update Post: {post.title}'
        context['title'] = f'Update-{post.title}'
        return context
    
    def get_success_url(self):
        messages.success(self.request, 'Post Updated successfully.')
        return super().get_success_url()
    
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        form.instance.author = self.request.user
        return super().form_valid(form)  
    
    def test_func(self) -> bool | None:
        post = self.get_object()
        return self.request.user == post.author
     

class PostDeleteView(UserPassesTestMixin, DeleteView):
    model = Post
    # success_url = reverse_lazy('home')
    
    def test_func(self) -> bool | None:
        post = self.get_object()
        return self.request.user == post.author
    
    def get_success_url(self):
        messages.success(self.request, 'Post deleted successfully.')
        return reverse_lazy('home')
    
class AboutView(TemplateView):
    template_name = 'blog_app/about.html'
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = 'About'
        return context
```

## URLs

The app defines URLs for the home page, post list, post creation, post detail, post update, post delete, and about page.

```python
from django.urls import path
from .views import (
    HomePageView,
    PostListView,
    PostCreateView,
    PostDetailView,
    PostUpdateView,
    PostDeleteView,
    AboutView,
)

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('posts/', PostListView.as_view(), name='post-list'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('posts/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('posts/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('posts/new/', PostCreateView.as_view(), name='post-new'),
]
```

# Django User Accounts App (*with codes*)

## Overview

This Django app provides user registration, authentication, and user profile management functionality. It includes features such as profile picture upload, date of birth, and user account updates.

## Table of Contents

- [Models](#models)
- [Forms](#forms)
- [Views](#views)
- [URLs](#urls)

## Models

### Imports

```python
# models.py
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from PIL import Image
```

### Profile Model
The `Profile` model extends the Django `User` model, adding fields for date of birth and profile picture.

```python
# models.py
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True, verbose_name = 'Date of birth') # verbose name is for display in admin interface and other forms
    profile_pic = models.ImageField(default='default_pic.png', upload_to='profile_pics')
    
    def __str__(self) -> str:
        return f'{self.user}'
    
    def get_absolute_url(self):
        """
        Define the absolute URL for a Profile object.

        This method is used by Django's generic views and other parts of the framework
        to determine the URL for a specific Profile object. By using the reverse()
        function, it generates the URL based on the 'profiles:profile-detail' URL pattern
        and includes the primary key (pk) of the object.

        Returns:
            str: The absolute URL for the Profile object.
        """
        return reverse('profiles:profile-detail', args=[str(self.pk)])
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            img = Image.open(self.profile_pic.path)

            # Set a maximum size for the profile picture
            max_size = (300, 300)
            if img.height > max_size[1] or img.width > max_size[0]:
                img.thumbnail(max_size)
                img.save(self.profile_pic.path)
        except Exception as e:
            print("Error occured while resizing image!", e)
```
### Forms
The app includes three forms for user registration, user updates, and profile updates.

```python
# forms.py
#imports
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['date_of_birth', 'profile_pic']
```

### Views
The app contains several views, including user registration, user profile display, user profile updates, and custom login view.

```python
# views.py
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
```

### URLs
The app defines URLs for user profiles, profile updates, user registration, login, logout, and password reset.

```python
# urls.py
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
```