from django.urls import path
from .views import (
    HomePageView,
    PostCreateView,
    PostDetailView,
    PostUpdateView,
    PostDeleteView,
)

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('posts/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('posts/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('post/new/', PostCreateView.as_view(), name='post-new'),
]