from rest_framework import generics, permissions, serializers
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
import logging

from .models import Photo, PhotoShare
from .serializers import PhotoSerializer, PhotoShareSerializer
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


class PhotoListCreateView(generics.ListCreateAPIView):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        try:
            user = request.user if hasattr(request, 'user') else None
            logger.debug('Photo upload request user=%s', getattr(user, 'username', user))
            logger.debug('Request CONTENT_TYPE=%s', request.META.get('CONTENT_TYPE'))
            logger.debug('Request data keys=%s', list(request.data.keys()))
        except Exception:
            logger.exception('Failed to log request info')

        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        owned_photos = Photo.objects.filter(owner=user)
        shared_photos = Photo.objects.filter(shares__shared_to=user)
        
        return (owned_photos | shared_photos).distinct()

    def perform_create(self, serializer):
        file = self.request.data.get('file')
        if not file:
            raise serializers.ValidationError({'file': 'No file provided'})
        original_name = file.name
        print(f"[DEBUG] Uploading file: {original_name} for user: {self.request.user.username}")
        photo = serializer.save(owner=self.request.user, original_name=original_name)
        print(f"[DEBUG] Successfully saved photo ID {photo.id} with file: {photo.file.name}")

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import FileResponse, HttpResponseForbidden, Http404
from django.conf import settings
import mimetypes
import os


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def protected_media(request, path):
    
    print("\n--- DEBUG: protected_media ---")
    print(f"1. Received request for path: {path}")
    
    try:
        photo = Photo.objects.get(file=path)
        print(f"2. [SUCCESS] Found photo in database: {photo.original_name}")
    except Photo.DoesNotExist:
        print(f"2. [ERROR] Http404! No Photo found in database with path: {path}")
        raise Http404()

    user = request.user
    owned = photo.owner == user
    shared = photo.shares.filter(shared_to=user).exists()
    
    if not (owned or shared):
        print(f"3. [ERROR] HttpResponseForbidden! Access denied. Owner: {owned}, Shared: {shared}")
        return HttpResponseForbidden('Access denied')
    
    print(f"3. [SUCCESS] Access granted. Owner: {owned}, Shared: {shared}")

    file_path = settings.MEDIA_ROOT / path
    print(f"4. Full file path: {file_path}")
    
    if not os.path.exists(str(file_path)):
        print(f"5. [ERROR] Http404! File DOES NOT EXIST on disk at path: {file_path}")
        raise Http404()
    
    print(f"5. [SUCCESS] File exists on disk.")

    content_type, _ = mimetypes.guess_type(str(file_path))
    return FileResponse(open(file_path, 'rb'), content_type=content_type)


class PhotoDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = PhotoSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        user = self.request.user
        return Photo.objects.filter(owner=user)

    def perform_destroy(self, instance):
        if instance.file:
            instance.file.delete(save=False)
        print(f"[DEBUG] Deleted photo ID {instance.id} ({instance.original_name}) by user {self.request.user.username}")
        instance.delete()


class PhotoShareView(generics.CreateAPIView):
    serializer_class = PhotoShareSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def perform_create(self, serializer):
        photo_id = self.request.data.get('photo')
        email_to_share = serializer.validated_data.get('shared_to')
        
        print(f"[DEBUG] Share request: photo_id={photo_id}, email={email_to_share}, from_user={self.request.user.username}")
        
        photo = get_object_or_404(Photo, id=photo_id, owner=self.request.user)
        print(f"[DEBUG] Photo found: {photo.original_name} (ID: {photo.id})")
        
        try:
            shared_to_user = User.objects.get(email=email_to_share)
            print(f"[DEBUG] Target user found: {shared_to_user.username} (email: {email_to_share})")
        except User.DoesNotExist:
            print(f"[DEBUG] User with email {email_to_share} not found!")
            raise
        
        photo_share = serializer.save(photo=photo, shared_to=shared_to_user)
        print(f"[DEBUG] Photo shared successfully! PhotoShare ID: {photo_share.id}")