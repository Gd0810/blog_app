from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_migrate
from django.dispatch import receiver

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

@receiver(post_migrate)
def create_default_categories(sender, **kwargs):
    if sender.name == 'blog':  # Ensure this runs only for the 'blog' app
        default_categories = [
            'Technology',
            'Lifestyle',
            'Travel',
            'Food',
            'Health',
            'Fashion',
            'Education',
            'Finance',
            'Entertainment',
            'Sports'
        ]
        for category_name in default_categories:
            Category.objects.get_or_create(name=category_name)

class Blog(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    published_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.blog}"

# blog/models.py
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    google_id = models.CharField(max_length=100, blank=True, null=True)  # Optional: Store Google user ID
    full_name = models.CharField(max_length=255, blank=True, null=True)  # Optional: Store Google name

    def __str__(self):
        return f"{self.user.username}'s profile"