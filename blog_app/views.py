from typing import Any
from django.db.models.query import QuerySet
from django.db import models
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect
from .models import Post, Like, Category, Comment
from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    UpdateView,
    DeleteView
    )
# Create your views here.

class HomePageView(ListView):
    model = Post
    template_name = 'blog_app/home.html'
    context_object_name = 'posts'
     
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = 'Home'
        context['recent_posts'] = Post.objects.all().order_by('-created_at')[:5]
        most_liked_posts = Post.objects.annotate(like_count=models.Count('likes')).order_by('-like_count')[:5]
        context['featured_posts'] = most_liked_posts
        context['categories'] = Category.objects.all()
        return context
    

class PostCreateView(CreateView):
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
    
    def post(self, request, *args, **kwargs):
        # Handling comment submission
        if 'comment_content' in self.request.POST:
            post = self.get_object()
            comment_content = self.request.POST['comment_content']
            Comment.objects.create(post=post, author=request.user, content=comment_content)
            messages.success(request, 'Comment added successfully.')
            return redirect('post-detail', pk=post.pk)

        # Handling like button click
        if 'like_button' in self.request.POST:
            post = self.get_object()
            # Check if the user already liked the post
            if not Like.objects.filter(post=post, user=request.user).exists():
                Like.objects.create(post=post, user=request.user)
                messages.success(request, 'Liked the post!')
            else:
                messages.warning(request, 'You have already liked this post.')
            return redirect('post-detail', pk=post.pk)

        return super().post(request, *args, **kwargs)
    
    
class PostUpdateView(UpdateView):
    model = Post
    fields = ['title', 'content', 'categories', 'is_published', 'cover_image']
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['header'] = 'Update Post'
        context['title'] = 'Update'
        return context
    
    def get_success_url(self):
        messages.success(self.request, 'Post Updated successfully.')
        return super().get_success_url()

class PostDeleteView(DeleteView):
    model = Post
    # success_url = reverse_lazy('home')
    
    def get_success_url(self):
        messages.success(self.request, 'Post deleted successfully.')
        return reverse_lazy('home')