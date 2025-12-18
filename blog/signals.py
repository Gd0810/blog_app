from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from allauth.account.signals import user_signed_up
from allauth.socialaccount.models import SocialAccount
from .models import UserProfile
import requests
from django.core.files.base import ContentFile

@receiver(user_signed_up)
def create_user_profile_on_social_signup(request, user, **kwargs):
    # Get or create UserProfile
    user_profile, created = UserProfile.objects.get_or_create(user=user)
    
    # If this is a social signup (e.g., Google), fetch extra data
    try:
        social_account = SocialAccount.objects.get(user=user, provider='google')
        extra_data = social_account.extra_data  # Google's profile data
        
        # Update User fields (optional: set username, email, name if needed)
        user.email = extra_data.get('email', user.email)
        if not user.first_name:
            user.first_name = extra_data.get('given_name', '')
        if not user.last_name:
            user.last_name = extra_data.get('family_name', '')
        user.save()
        
        # Fetch and save Google profile picture
        picture_url = extra_data.get('picture')
        if picture_url and not user_profile.profile_picture:
            # Download the image
            response = requests.get(picture_url)
            if response.status_code == 200:
                # Save image to profile_picture field
                filename = f"{user.username}_google_profile.jpg"
                user_profile.profile_picture.save(filename, ContentFile(response.content), save=True)
        
        # Optional: Save additional fields if added to UserProfile
        user_profile.google_id = extra_data.get('id', '')
        user_profile.full_name = extra_data.get('name', '')
        user_profile.save()
    
    except SocialAccount.DoesNotExist:
        # Non-social signup; just ensure UserProfile exists
        pass

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)