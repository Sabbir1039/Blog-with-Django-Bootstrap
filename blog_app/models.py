from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
from PIL import Image
from django.urls import reverse

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
    cover_image = models.ImageField(default='cover.jpg', upload_to='cover_pics')
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})

@receiver(pre_save, sender=Post)
def resize_cover_image(sender, instance, **kwargs):
    if instance.cover_image:
        img = Image.open(instance.cover_image.path)

        # Define the desired size for your image
        max_size = (800, 600)

        # Resize the image while preserving its aspect ratio
        img.thumbnail(max_size)

        # Save the resized image back to the same path
        img.save(instance.cover_image.path)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {str(self.author)} on {str(self.post)}"

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('post', 'user')  # Ensure each user can only like a post once.

    def __str__(self):
        return f"Like by {self.user} on {self.post}"