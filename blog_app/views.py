from typing import Any
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Post
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
        # context['posts'] = Post.objects.all().order_by('created_at')[:5]
        # context['top_post'] = Post.objects.all().count()
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