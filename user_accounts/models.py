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
        """
        Define the absolute URL for a Profile object.

        This method is used by Django's generic views and other parts of the framework
        to determine the URL for a specific Profile object. By using the reverse()
        function, it generates the URL based on the 'profiles:profile-detail' URL pattern
        and includes the primary key (pk) of the object.

        Returns:
            str: The absolute URL for the Profile object.
        """
        return reverse('profiles:profile-detail', args=[str(self.pk)])