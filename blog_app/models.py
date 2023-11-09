from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    categories = models.ManyToManyField(Category, related_name='posts')
    is_published = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('post', 'user')  # Ensure each user can only like a post once.

    def __str__(self):
        return f"Like by {self.user} on {self.post}"