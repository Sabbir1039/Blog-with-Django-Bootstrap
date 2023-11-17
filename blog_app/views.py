from typing import Any
from django.db.models.query import QuerySet
from django.db import models
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect
from .models import Post, Like, Category, Comment
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    UpdateView,
    DeleteView
    )

# views here.

class HomePageView(ListView):
    model = Post
    template_name = 'blog_app/home.html'
    context_object_name = 'posts'
     
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = 'Blog Home'
        context['recent_posts'] = Post.objects.all().order_by('-created_at')[:5]
        most_liked_posts = Post.objects.annotate(like_count=models.Count('likes')).order_by('-like_count')[:3]
        context['featured_posts'] = most_liked_posts
        context['categories'] = Category.objects.all()
        return context
    
class PostListView(ListView):
    model = Post
    context_object_name = "posts"
    paginate_by = 3
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = "All Posts"
        context['categories'] = Category.objects.all()
        return context
    
    def get_queryset(self) -> QuerySet[Any]:
        queryset = super().get_queryset()
        category_id = self.request.GET.get('category')
        search_query = self.request.GET.get('search')
        
        # Apply category filter
        if category_id:
            queryset = queryset.filter(categories__id = category_id)
            
        # Apply search filter
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)
        return queryset
            

class PostCreateView(LoginRequiredMixin,CreateView):
    model = Post
    fields = ['title', 'content', 'categories', 'is_published', 'cover_image']
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['header'] = 'Create New Post'
        context['title'] = 'New Post'
        return context
    
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        try:
            # Additional validation for uploaded files
            cover_image = form.cleaned_data.get('cover_image')
            if cover_image:
                # Ensure that only specific file types are allowed
                allowed_file_types = ['image/jpeg', 'image/png']
                if cover_image.content_type not in allowed_file_types:
                    form.add_error('cover_image', 'Only JPEG and PNG images are allowed.')

                # Check for a valid file name (you can customize this based on your requirements)
                if not cover_image.name.lower().endswith(('.jpg', '.jpeg', '.png')):
                    form.add_error('cover_image', 'Invalid file type. Only JPEG and PNG files are allowed.')

            form.instance.author = self.request.user
            return super().form_valid(form)

        except Exception as e:
            # Handle the exception here, you can log the error or take appropriate actions
            # For example:
            # logger.error(f"An error occurred: {e}")
            form.add_error(None, 'An error occurred while processing the form.')
            return self.form_invalid(form)     
    

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
    
    
class PostUpdateView(UpdateView):
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
        try:
            # Additional validation for uploaded files
            cover_image = form.cleaned_data.get('cover_image')
            if cover_image:
                # Ensure that only specific file types are allowed
                allowed_file_types = ['image/jpeg', 'image/png']
                if cover_image.content_type not in allowed_file_types:
                    form.add_error('cover_image', 'Only JPEG and PNG images are allowed.')

                # Check for a valid file name (you can customize this based on your requirements)
                if not cover_image.name.lower().endswith(('.jpg', '.jpeg', '.png')):
                    form.add_error('cover_image', 'Invalid file type. Only JPEG and PNG files are allowed.')

            form.instance.author = self.request.user
            return super().form_valid(form)

        except Exception as e:
            # Handle the exception here, you can log the error or take appropriate actions
            # For example:
            # logger.error(f"An error occurred: {e}")
            form.add_error(None, 'An error occurred while processing the form.')
            return self.form_invalid(form)

class PostDeleteView(DeleteView):
    model = Post
    # success_url = reverse_lazy('home')
    
    def get_success_url(self):
        messages.success(self.request, 'Post deleted successfully.')
        return reverse_lazy('home')