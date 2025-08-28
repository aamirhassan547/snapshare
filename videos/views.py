from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Avg
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Video, Comment, Rating
from .forms import VideoUploadForm, CommentForm, RatingForm
from users.models import CustomUser
import os

def home(request):
    latest_videos = Video.objects.select_related('creator').order_by('-upload_date')[:10]
    return render(request, 'videos/home.html', {'latest_videos': latest_videos})

@login_required
def upload_video(request):
    if not request.user.is_creator():
        messages.error(request, 'Only creators can upload videos.')
        return redirect('home')
   
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.creator = request.user
            video.save()
            messages.success(request, 'Video uploaded successfully!')
            return redirect('video_detail', video_id=video.id)
    else:
        form = VideoUploadForm()
    return render(request, 'videos/upload.html', {'form': form})

def video_detail(request, video_id):
    video = get_object_or_404(Video.objects.select_related('creator'), id=video_id)
    
    # Fetch comments with pagination
    comments = video.comments.select_related('user').order_by('-created_at')
    paginator = Paginator(comments, 10)  # 10 comments per page
    page_number = request.GET.get('page', 1)
    comments_page = paginator.get_page(page_number)
    
    # Calculate average rating
    average_rating = video.ratings.aggregate(Avg('rating'))['rating__avg']
    
    # Fetch other videos by the creator (excluding the current video)
    creator_videos = video.creator.videos.select_related('creator').exclude(id=video.id).order_by('-upload_date')[:3]
    
    # Increment view count
    video.views += 1
    video.save()
   
    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        rating_form = RatingForm(request.POST)
       
        if 'comment_submit' in request.POST and comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.video = video
            comment.user = request.user
            comment.save()
            messages.success(request, 'Comment posted successfully!')
            return redirect('video_detail', video_id=video.id)
       
        if 'rating_submit' in request.POST and rating_form.is_valid():
            rating, created = Rating.objects.update_or_create(
                video=video,
                user=request.user,
                defaults={'rating': rating_form.cleaned_data['rating']}
            )
            messages.success(request, 'Rating submitted successfully!')
            return redirect('video_detail', video_id=video.id)
    else:
        comment_form = CommentForm()
        rating_form = RatingForm()
   
    # Check if user has already rated and liked
    user_rating = None
    is_liked = False
    if request.user.is_authenticated:
        try:
            user_rating = Rating.objects.get(video=video, user=request.user).rating
        except Rating.DoesNotExist:
            pass
       
        is_liked = video.likes.filter(id=request.user.id).exists()
   
    return render(request, 'videos/detail.html', {
        'video': video,
        'comments': comments_page,
        'comment_form': comment_form,
        'rating_form': rating_form,
        'average_rating': average_rating,
        'user_rating': user_rating,
        'is_liked': is_liked,
        'total_likes': video.total_likes(),
        'creator_videos': creator_videos,
    })

@require_POST
@login_required
def like_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    if video.likes.filter(id=request.user.id).exists():
        video.likes.remove(request.user)
        liked = False
    else:
        video.likes.add(request.user)
        liked = True
   
    return JsonResponse({
        'liked': liked,
        'total_likes': video.total_likes()
    })

def get_azure_media_url(file_field):
    """Helper function to get Azure Blob Storage URL for media files"""
    if not file_field:
        return None
    
    # If using Azure Storage, the file_field.url will already be the Azure URL
    # due to our DEFAULT_FILE_STORAGE setting
    return file_field.url

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def video_list_api(request):
    videos = Video.objects.select_related('creator').order_by('-upload_date')
    paginator = Paginator(videos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
   
    data = {
        'videos': [
            {
                'id': video.id,
                'title': video.title,
                'description': video.description,
                'thumbnail_url': get_azure_media_url(video.thumbnail),
                'creator': video.creator.username,
                'views': video.views,
                'likes': video.total_likes(),
                'upload_date': video.upload_date,
            }
            for video in page_obj
        ],
        'count': paginator.count,
        'num_pages': paginator.num_pages,
    }
    return JsonResponse(data)

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def video_detail_api(request, video_id):
    video = get_object_or_404(Video.objects.select_related('creator'), id=video_id)
    comments = video.comments.select_related('user').order_by('-created_at')
    ratings = video.ratings.all()
   
    data = {
        'video': {
            'id': video.id,
            'title': video.title,
            'description': video.description,
            'video_url': get_azure_media_url(video.video_file),
            'thumbnail_url': get_azure_media_url(video.thumbnail),
            'creator': {
                'id': video.creator.id,
                'username': video.creator.username,
            },
            'publisher': video.publisher,
            'producer': video.producer,
            'genre': video.get_genre_display(),
            'age_rating': video.get_age_rating_display(),
            'views': video.views,
            'likes': video.total_likes(),
            'upload_date': video.upload_date,
        },
        'comments': [
            {
                'id': comment.id,
                'user': comment.user.username,
                'text': comment.text,
                'created_at': comment.created_at,
            }
            for comment in comments
        ],
        'average_rating': ratings.aggregate(Avg('rating'))['rating__avg'],
        'rating_count': ratings.count(),
    }
    return JsonResponse(data)