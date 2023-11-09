from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True, verbose_name = 'Date of Birth')
    profile_pic = models.ImageField(default='default_pic.png', upload_to='profile_pics')
    
    def __str__(self) -> str:
        return f'{self.user}'
    
    def get_absolute_url(self):
        return reverse('profiles:profile-detail', args=[str(self.pk)])