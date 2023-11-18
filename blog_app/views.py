from typing import Any
from django.db.models.query import QuerySet
from django.db import models
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.http import Http404


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
    DeleteView
    )

import logging

logger = logging.getLogger(__name__)


# views here.
class HomePageView(ListView):
    model = Post
    template_name = 'blog_app/home.html'
    context_object_name = 'posts'
     
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
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
    
   
    