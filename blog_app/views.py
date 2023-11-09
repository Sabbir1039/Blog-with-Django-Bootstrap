from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render
from .models import Post
from django.views.generic.list import ListView
# Create your views here.

class HomePageView(ListView):
    model = Post
    template_name = 'blog_app/home.html'
    # context_object_name = 'posts'
    
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = 'Home'
        context['recent_post'] = Post.objects.all().order_by('created_at')[:5]
        # context['top_post'] = Post.objects.all().count()
        return context