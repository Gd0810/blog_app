from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import Blog, Category, Comment, UserProfile
from .forms import CustomUserCreationForm, CustomAuthenticationForm, BlogForm, CommentForm, UserProfileForm
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

def home(request):
    blogs = Blog.objects.all().order_by('-published_date')
    return render(request, 'blog/home.html', {'blogs': blogs})

def blog_detail(request, id):
    blog = get_object_or_404(Blog, id=id)
    comments = blog.comments.all()
    related_blogs = Blog.objects.filter(category=blog.category).exclude(id=blog.id)[:3]
    comment_form = CommentForm() if request.user.is_authenticated else None

    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.blog = blog
            comment.author = request.user
            comment.save()
            messages.success(request, 'Comment posted successfully!')
            return redirect('blog_detail', id=blog.id)

    return render(request, 'blog/blog_detail.html', {
        'blog': blog,
        'comments': comments,
        'related_blogs': related_blogs,
        'comment_form': comment_form
    })

@login_required
def account_settings(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    blogs = Blog.objects.filter(author=request.user)
    comments = Comment.objects.filter(blog__author=request.user)
    blog_form = BlogForm()
    profile_form = UserProfileForm(instance=user_profile)
    update_form = BlogForm()

    if request.method == 'POST':
        logger.info(
            "account_settings POST user_id=%s username=%s action_keys=%s file_keys=%s",
            request.user.id,
            request.user.username,
            [k for k in request.POST.keys() if k != 'csrfmiddlewaretoken'],
            list(request.FILES.keys()),
        )
        if 'blog_submit' in request.POST:
            blog_form = BlogForm(request.POST, request.FILES)
            if blog_form.is_valid():
                blog = blog_form.save(commit=False)
                blog.author = request.user
                blog.save()
                logger.info("Blog created user_id=%s blog_id=%s", request.user.id, blog.id)
                messages.success(request, 'Blog created successfully!')
                return redirect('account_settings')
            logger.warning("Blog create failed user_id=%s errors=%s", request.user.id, blog_form.errors.as_json())
            messages.error(request, f'Could not create blog. Errors: {blog_form.errors.as_text()}')
        elif 'profile_submit' in request.POST:
            profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
            if profile_form.is_valid():
                profile_form.save()
                logger.info("Profile updated user_id=%s has_picture=%s", request.user.id, bool(user_profile.profile_picture))
                messages.success(request, 'Profile updated successfully!')
                return redirect('account_settings')
            logger.warning("Profile update failed user_id=%s errors=%s", request.user.id, profile_form.errors.as_json())
            messages.error(request, f'Could not update profile. Errors: {profile_form.errors.as_text()}')
        elif 'update_blog' in request.POST:
            blog_id = request.POST.get('blog_id')
            blog = get_object_or_404(Blog, id=blog_id, author=request.user)
            update_form = BlogForm(request.POST, request.FILES, instance=blog)
            if update_form.is_valid():
                update_form.save()
                logger.info("Blog updated user_id=%s blog_id=%s", request.user.id, blog.id)
                messages.success(request, 'Blog updated successfully!')
                return redirect('account_settings')
            logger.warning("Blog update failed user_id=%s blog_id=%s errors=%s", request.user.id, blog_id, update_form.errors.as_json())
            messages.error(request, f'Could not update blog. Errors: {update_form.errors.as_text()}')
        elif 'delete_blog' in request.POST:
            blog_id = request.POST.get('blog_id')
            blog = get_object_or_404(Blog, id=blog_id, author=request.user)
            blog.delete()
            logger.info("Blog deleted user_id=%s blog_id=%s", request.user.id, blog_id)
            messages.success(request, 'Blog deleted successfully!')
            return redirect('account_settings')
        else:
            logger.warning("account_settings unknown POST action user_id=%s keys=%s", request.user.id, list(request.POST.keys()))

    return render(request, 'blog/account_settings.html', {
        'user_profile': user_profile,
        'blogs': blogs,
        'comments': comments,
        'blog_form': blog_form,
        'profile_form': profile_form,
        'update_form': update_form
    })

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'blog/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('home')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'blog/login.html', {'form': form})

from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages

def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('home')  # Or use allauth's LOGOUT_REDIRECT_URL
