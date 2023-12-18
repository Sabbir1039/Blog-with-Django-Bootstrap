# Full Featured Blog Web App with Django+Bootstrap

Welcome to the full featured django blog web app, a versatile web application that provides a robust blogging platform with user registration, authentication, and profile management features. This project is built using the Django web framework and Bootstrap, making it scalable, secure, and customizable for various blogging needs.

## Introduction

This Django project combines two essential components:

- [Blog App:](#django-blog-app-explanation) Allows users to create, edit, and delete blog posts, categorize them, leave comments, and like posts.
- [User Accounts App:](#django-user-accounts-app) Provides user registration, authentication, reset user password with email and profile management functionalities, including the option to upload profile pictures.

## Project Structure

The project follows a modular structure to enhance maintainability and organization. Below is a sample project structure to will help navigate the codebase effectively:

```plaintext
django_blog_and_user_accounts/
|-- blog_app/
|   |-- migrations/
|   |-- static/
|   |-- templates/
|   |-- __init__.py
|   |-- admin.py
|   |-- apps.py
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
## Installation
### Prerequisites
- [Python](https://www.python.org/downloads/) (3.6 or higher)
- [pip](https://pip.pypa.io/en/stable/installation/)

#### Create Virtual Environment (Optional but Recommended)
  ```bash
  python -m venv venv
  ```
#### Activate the virtual environment:
- On Windows:
  ```bash
  venv\Scripts\activate
  ```
- On macOS/Linux:
  ```bash
  source venv/bin/activate
  ```
#### Install Dependencies
```bash
pip install -r requirements.txt
```
#### Project Configuration
- Set Up Database
    ```bash
    python manage.py migrate
    ```
- Create Superuser (Optional)
  ```bash
  python manage.py createsuperuser
  ```
- Run the Development Server
  ```bash
  python manage.py runserver
  ```


## Django Blog App Explanation

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

The `Category` model represents a blog post category, featuring a unique name with a maximum length of 200 characters. It includes an optional description field for additional context. This model is essential for organizing and categorizing blog posts.

### Post Model

The `Post` model represents a blog post with the following attributes:

- `title`: The title of the post.
- `content`: The main content of the post.
- `created_at`: The timestamp when the post was created.
- `updated_at`: The timestamp when the post was last updated.
- `author`: The author of the post, linked to the User model.
- `categories`: Many-to-many relationship with the Category model, allowing posts to belong to multiple categories.
- `is_published`: A boolean field indicating whether the post is published (default is True).
- `cover_image`: An image field for the post's cover image, with a default image and uploaded to the 'cover_pics' directory.

##### Methods

- `__str__()`: Returns the title of the post.
- `get_absolute_url()`: Returns the absolute URL for the post detail view.

##### Meta

- The model is ordered by `-created_at` in descending order by default.

##### Save Method

- The `save()` method resizes the cover image to a maximum size (1080x620) before saving the post.

Note: Ensure you have included the `Post` model in your project's `models.py` file and have run migrations to apply changes to the database.

### Comment Model

The `Comment` model represents a comment on a blog post with the following attributes:

- `post`: The post to which the comment is associated, linked to the Post model.
- `author`: The author of the comment, linked to the User model.
- `content`: The content of the comment.
- `created_at`: The timestamp when the comment was created.

##### Methods

- `__str__()`: Returns a string representation of the comment mentioning the author and the post.


### Like Model

The `Like` model represents a user's like on a blog post with the following attributes:

- `post`: The post that is liked, linked to the Post model.
- `user`: The user who liked the post, linked to the User model.

##### Meta

- Ensures each user can only like a post once by specifying `unique_together = ('post', 'user')`.



## Views

The app contains various views, including the home page, post list, post creation, post detail, post update, post delete, and an about page.

### Imports
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
```
## HomePageView

The `HomePageView` is a Django class-based view that extends `ListView` to display a list of blog posts on the home page.

##### Attributes

- `model`: Specifies the model used for the view (`Post` model in this case).
- `template_name`: Defines the template used to render the view ('blog_app/home.html').
- `context_object_name`: Sets the variable name for the list of posts in the template ('posts').

##### Methods

##### `get_context_data()`

- Overrides the `get_context_data` method to provide additional context data for rendering the template.
- Sets attributes such as `title`, `recent_posts`, `featured_posts`, and `categories` for dynamic content.
- Handles exceptions for potential errors during data retrieval and logging.

## PostListView

The `PostListView` is a Django class-based view extending `ListView` to display a paginated list of blog posts.

##### Attributes

- `model`: Specifies the model used for the view (`Post` model).
- `context_object_name`: Sets the variable name for the list of posts in the template ('posts').
- `paginate_by`: Determines the number of posts to display per page (3 in this case).

##### Methods

##### `get_context_data()`

- Overrides the `get_context_data` method to provide additional context data for rendering the template.
- Extracts URL parameters such as 'category' and 'search' to filter posts accordingly.
- Handles exceptions during data retrieval and logging.

##### `get_queryset()`

- Overrides the `get_queryset` method to filter the queryset based on 'category' and 'search' parameters.
- Applies category and search filters to the queryset.
- Handles exceptions during queryset retrieval and logging.

## PostCreateView

The `PostCreateView` is a Django class-based view extending `CreateView` to handle the creation of new blog posts.

##### Attributes

- `model`: Specifies the model used for the view (`Post` model).
- `fields`: Determines the fields from the model that should be included in the form.

##### Methods

##### `get_context_data()`

- Overrides the `get_context_data` method to provide additional context data for rendering the template.
- Sets attributes such as `header` and `title` for a new post creation.

##### `form_valid()`

- Overrides the `form_valid` method to set the post author as the current logged-in user before form submission.

## PostDetailView

The `PostDetailView` is a Django class-based view extending `DetailView` to display detailed information about a single blog post.

##### Attributes

- `model`: Specifies the model used for the view (`Post` model).
- `context_object_name`: Sets the variable name for the post object in the template ('post').

##### Methods

##### `get_context_data()`

- Overrides the `get_context_data` method to provide additional context data for rendering the template.
- Checks if the current user has liked the post and sets the `is_liked` attribute accordingly.
- Sets the title attribute based on the post title.

##### `post()`

- Handles POST requests, allowing users to submit comments and like the post.
- Checks user authentication status before processing actions.
- Handles comment submission and like button clicks, providing appropriate feedback messages.

## PostUpdateView

The `PostUpdateView` is a Django class-based view extending `UpdateView` to handle the updating of existing blog posts.

##### Attributes

- `model`: Specifies the model used for the view (`Post` model).
- `fields`: Determines the fields from the model that should be included in the update form.

##### Methods

##### `get_context_data()`

- Overrides the `get_context_data` method to provide additional context data for rendering the template.
- Sets attributes such as `header` and `title` for updating a specific post.

##### `get_success_url()`

- Overrides the `get_success_url` method to set a success message upon updating the post.

##### `form_valid()`

- Overrides the `form_valid` method to set the post author as the current logged-in user before form submission.

##### `test_func()`

- Overrides the `test_func` method from `UserPassesTestMixin` to check if the current user is the author of the post being updated.

## PostDeleteView

The `PostDeleteView` is a Django class-based view extending `DeleteView` to handle the deletion of existing blog posts.

##### Attributes

- `model`: Specifies the model used for the view (`Post` model).

##### Methods

##### `test_func()`

- Overrides the `test_func` method from `UserPassesTestMixin` to check if the current user is the author of the post being deleted.

##### `get_success_url()`

- Overrides the `get_success_url` method to set a success message upon deleting the post and redirecting to the home page.

## AboutView

The `AboutView` is a Django class-based view extending `TemplateView` to render an about page.

##### Attributes

- `template_name`: Specifies the template used for rendering the view ('blog_app/about.html').

##### Methods

##### `get_context_data()`

- Overrides the `get_context_data` method to provide additional context data for rendering the template.
- Sets the `title` attribute for the about page.


## Logging Configuration

The `logger` is an instance of the Python `logging` module configured for the current module (`__name__`).

##### Usage

We can use the `logger` to record log messages throughout our application. For example:

```python
# Example usage
try:
    # Some code that might raise an exception
    result = perform_complex_operation()
except Exception as e:
    # Log the exception
    logger.error(f"An error occurred: {e}")
    # Additional handling or re-raising the exception as needed
```

## URL Patterns

The `urlpatterns` list contains the URL patterns for Django blog app. Each pattern is associated with a specific view.

### Views and URLs

1. **Home Page:**
    - View: `HomePageView`
    - URL: `/`
    - Name: `home`

2. **About Page:**
    - View: `AboutView`
    - URL: `/about/`
    - Name: `about`

3. **List of Posts:**
    - View: `PostListView`
    - URL: `/posts/`
    - Name: `post-list`

4. **Post Detail:**
    - View: `PostDetailView`
    - URL: `/posts/<int:pk>/`
    - Name: `post-detail`

5. **Update Post:**
    - View: `PostUpdateView`
    - URL: `/posts/<int:pk>/update/`
    - Name: `post-update`

6. **Delete Post:**
    - View: `PostDeleteView`
    - URL: `/posts/<int:pk>/delete/`
    - Name: `post-delete`

7. **Create New Post:**
    - View: `PostCreateView`
    - URL: `/posts/new/`
    - Name: `post-new`

### Usage

To navigate between different pages, use the provided URLs and view names in Django templates or in application's code.

```python
# Example URL mapping in a Django template
<a href="{% url 'home' %}">Home</a>
```


# Django User Accounts App

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
## Profile Model

The `Profile` model extends the built-in `User` model in Django to include additional user information.

#### Fields

- `user`: One-to-One relationship with the `User` model, linking the profile to a specific user.
- `date_of_birth`: Date field representing the user's date of birth (nullable and optional).
- `profile_pic`: Image field for the user's profile picture, with a default image and uploaded to the 'profile_pics' directory.

#### Methods

#### `__str__()`

- Returns a string representation of the profile, using the associated user's username.

#### `get_absolute_url()`

- Defines the absolute URL for a `Profile` object.
- Used by Django's generic views and other parts of the framework to determine the URL for a specific profile object.
- Generates the URL based on the 'profiles:profile-detail' URL pattern and includes the primary key (pk) of the object.

#### `save()`

- Overrides the `save` method to resize the profile picture to a maximum size (300x300) before saving the profile.

## User Registration Form (UserRegisterForm)

The `UserRegisterForm` is a Django form for user registration, extending `UserCreationForm` and adding an email field.

#### Fields

- `username`: Required field for the username.
- `email`: Required email field.
- `password1` and `password2`: Required fields for password entry and confirmation.


## Views
The app contains several views, including user registration, user profile display, user profile updates, and custom login view.

### Imports
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
```

### User Registration View (UserRegistrationView)

The `UserRegistrationView` is a Django class-based view extending `CreateView` for user registration.

#### Attributes

- `form_class`: Specifies the form used for user registration (`UserRegisterForm`).
- `template_name`: Defines the template used for rendering the view ('user_accounts/register.html').
- `context_object_name`: Sets the variable name for the form in the template ('form').
- `success_url`: URL to redirect to upon successful user registration ('/login/').

#### Methods

#### `get_context_data()`

- Overrides the `get_context_data` method to provide additional context data for rendering the template.
- Sets the `title` attribute for the registration page.

#### `form_valid()`

- Overrides the `form_valid` method to perform additional actions after the form is successfully validated.
- Creates a corresponding `Profile` instance for the registered user.
- Displays a success message and redirects the user to the login page.

#### `dispatch()`

- Overrides the `dispatch` method to prevent already authenticated users from accessing the registration page.
- Redirects authenticated users to the home page.


### User Profile View (UserProfileView)

The `UserProfileView` is a Django class-based view extending `DetailView` to display user profile information.

#### Attributes

- `model`: Specifies the model used for the view (`Profile` model).
- `template_name`: Defines the template used for rendering the view ('user_accounts/user_profile.html').

#### Methods

#### `get_context_data()`

- Overrides the `get_context_data` method to provide additional context data for rendering the template.
- Sets the `title` attribute based on the associated user's username.

#### `get_object()`

- Overrides the `get_object` method to ensure that the user can only view their own profile.
- Retrieves the profile associated with the currently logged-in user.


### User Profile Update View (UserProfileUpdateView)

The `UserProfileUpdateView` is a Django class-based view extending `UpdateView` to handle the updating of user profile information.

#### Attributes

- `model`: Specifies the model used for the view (`Profile` model).
- `form_class`: Specifies the form used for updating user information (`UserUpdateForm`).
- `template_name`: Defines the template used for rendering the view ('user_accounts/user_profile_update.html').

#### Methods

#### `get_success_url()`

- Overrides the `get_success_url` method to determine the URL to redirect to upon successful profile update.
- Redirects to the user's profile detail page.

#### `get_object()`

- Overrides the `get_object` method to ensure that the user can only update their own profile.
- Retrieves the profile associated with the currently logged-in user.

#### `get_context_data()`

- Overrides the `get_context_data` method to provide additional context data for rendering the template.
- Retrieves the user's profile and includes the `ProfileUpdateForm` instance in the context.
- Sets the `title` attribute for updating the user's profile.

#### `post()`

- Overrides the `post` method to handle form submission for updating user information.
- Validates both the `UserUpdateForm` and `ProfileUpdateForm`.
- Displays success or error messages accordingly.

### Custom Login View (MyLoginView)

The `MyLoginView` is a Django class-based view extending `LoginView` to customize the behavior of the login process.

#### Attributes

- `redirect_authenticated_user`: If set to `True`, redirects authenticated users to the home page upon attempting to access the login page.
- `template_name`: Defines the template used for rendering the view ('user_accounts/login.html').

#### Methods

#### `get_success_url()`

- Overrides the `get_success_url` method to determine the URL to redirect to upon successful login.
- Redirects authenticated users to the home page.

#### `form_invalid()`

- Overrides the `form_invalid` method to handle the case where the login form is invalid.
- Displays an error message for invalid username or password.



## User Accounts URLs

The `urlpatterns` list contains the URL patterns for user accounts functionality in your Django project.

### User Profile URLs

1. **Profile Detail:**
    - View: `UserProfileView`
    - URL: `/profile/<int:pk>/`
    - Name: `profile-detail`

2. **Update User Profile:**
    - View: `UserProfileUpdateView`
    - URL: `/profile/<int:pk>/update/`
    - Name: `user_profile_update`

### User Authentication URLs

3. **User Registration:**
    - View: `UserRegistrationView`
    - URL: `/register/`
    - Name: `register`

4. **User Login:**
    - View: `MyLoginView`
    - URL: `/login/`
    - Name: `login`

5. **User Logout:**
    - View: `auth_views.LogoutView`
    - URL: `/logout/`
    - Name: `logout`

### Password Reset URLs

6. **Password Reset:**
    - View: `auth_views.PasswordResetView`
    - URL: `/password-reset/`
    - Name: `password_reset`

7. **Password Reset Done:**
    - View: `auth_views.PasswordResetDoneView`
    - URL: `/password-reset/done/`
    - Name: `password_reset_done`

8. **Password Reset Confirm:**
    - View: `auth_views.PasswordResetConfirmView`
    - URL: `/password-reset-confirm/<uidb64>/<token>/`
    - Name: `password_reset_confirm`

9. **Password Reset Complete:**
    - View: `auth_views.PasswordResetCompleteView`
    - URL: `/password-reset-complete/`
    - Name: `password_reset_complete`

### Usage

To navigate between different pages or include these URLs in templates, use the provided URL patterns and names.

```python
# Example URL mapping in a Django template
<a href="{% url 'profile-detail' pk=user.id %}">View Profile</a>
