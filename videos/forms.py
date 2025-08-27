from django import forms
from .models import Video, Comment, Rating

class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = [
            'title', 'description', 'video_file', 'thumbnail', 
            'publisher', 'producer', 'genre', 'age_rating'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add a comment...'}),
        }

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating']
        widgets = {
            'rating': forms.NumberInput(attrs={
                'min': 1, 
                'max': 5,
                'class': 'rating-input'
            }),
        }