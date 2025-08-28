from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_video, name='upload_video'),
    path('video/<int:video_id>/', views.video_detail, name='video_detail'),
    path('video/<int:video_id>/like/', views.like_video, name='like_video'),
    path('api/videos/', views.video_list_api, name='video_list_api'),
    path('api/videos/<int:video_id>/', views.video_detail_api, name='video_detail_api'),
    path('get-azure-sas-token/', views.get_azure_sas_token, name='get_azure_sas_token'),

]
