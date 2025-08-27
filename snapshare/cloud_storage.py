from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings

class MediaStorage(S3Boto3Storage):
    location = 'media'
    file_overwrite = False

def get_storage():
    if settings.DEBUG:
        return None  # Use default file system storage in development
    return MediaStorage()
