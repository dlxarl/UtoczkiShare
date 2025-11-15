from rest_framework import generics, permissions, serializers
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
import logging

from .models import Photo, PhotoShare
from .serializers import PhotoSerializer, PhotoShareSerializer
from django.contrib.auth.models import User # Потрібно для пошуку за email

logger = logging.getLogger(__name__)


class PhotoListCreateView(generics.ListCreateAPIView):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    # accept multipart form uploads
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        # Log helpful debugging info to server logs for failed uploads
        try:
            user = request.user if hasattr(request, 'user') else None
            logger.debug('Photo upload request user=%s', getattr(user, 'username', user))
            logger.debug('Request CONTENT_TYPE=%s', request.META.get('CONTENT_TYPE'))
            logger.debug('Request data keys=%s', list(request.data.keys()))
        except Exception:
            logger.exception('Failed to log request info')

        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        """
        Повертає фото, де користувач є власником,
        АБО фото, якими з ним поділилися.
        """
        user = self.request.user
        owned_photos = Photo.objects.filter(owner=user)
        shared_photos = Photo.objects.filter(shares__shared_to=user)
        
        # Об'єднуємо два набори запитів і повертаємо унікальні результати
        return (owned_photos | shared_photos).distinct()

    def perform_create(self, serializer):
        file = self.request.data.get('file')
        if not file:
            # ensure a clear error is returned when file is missing
            raise serializers.ValidationError({'file': 'No file provided'})
        original_name = file.name
        print(f"[DEBUG] Uploading file: {original_name} for user: {self.request.user.username}")
        photo = serializer.save(owner=self.request.user, original_name=original_name)
        print(f"[DEBUG] Successfully saved photo ID {photo.id} with file: {photo.file.name}")

    # Protected media serving for photos. This endpoint requires authentication
    # and will return the file only if the requesting user is the owner or the
    # photo has been explicitly shared with them.
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
    
    # --- ПОЧАТОК БЛОКУ ДЛЯ ДЕБАГУ ---
    print("\n--- DEBUG: protected_media ---")
    print(f"1. Отримано запит на шлях (path): {path}")
    
    try:
        photo = Photo.objects.get(file=path)
        print(f"2. [УСПІХ] Знайдено фото в базі: {photo.original_name}")
    except Photo.DoesNotExist:
        print(f"2. [ПОМИЛКА] Http404! Не знайдено Photo в базі даних зі шляхом: {path}")
        raise Http404()

    user = request.user
    owned = photo.owner == user
    shared = photo.shares.filter(shared_to=user).exists()
    
    if not (owned or shared):
        print(f"3. [ПОМИЛКА] HttpResponseForbidden! Доступ заборонено. Власник: {owned}, Спільний: {shared}")
        return HttpResponseForbidden('Access denied')
    
    print(f"3. [УСПІХ] Доступ дозволено. Власник: {owned}, Спільний: {shared}")

    file_path = settings.MEDIA_ROOT / path
    print(f"4. Повний шлях до файлу: {file_path}")
    
    if not os.path.exists(str(file_path)):
        print(f"5. [ПОМИЛКА] Http404! Файл НЕ ІСНУЄ на диску за шляхом: {file_path}")
        raise Http404()
    
    print(f"5. [УСПІХ] Файл існує на диску.")
    # --- КІНЕЦЬ БЛОКУ ДЛЯ ДЕБАГУ ---

    content_type, _ = mimetypes.guess_type(str(file_path))
    return FileResponse(open(file_path, 'rb'), content_type=content_type)


class PhotoDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = PhotoSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        # Only allow users to delete their own photos (not shared photos)
        user = self.request.user
        return Photo.objects.filter(owner=user)

    def perform_destroy(self, instance):
        # Delete the actual file from disk before deleting the database record
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
        
        # Get the photo (must be owned by current user)
        photo = get_object_or_404(Photo, id=photo_id, owner=self.request.user)
        print(f"[DEBUG] Photo found: {photo.original_name} (ID: {photo.id})")
        
        # Get the user to share with
        try:
            shared_to_user = User.objects.get(email=email_to_share)
            print(f"[DEBUG] Target user found: {shared_to_user.username} (email: {email_to_share})")
        except User.DoesNotExist:
            print(f"[DEBUG] User with email {email_to_share} not found!")
            raise
        
        # Save the share
        photo_share = serializer.save(photo=photo, shared_to=shared_to_user)
        print(f"[DEBUG] Photo shared successfully! PhotoShare ID: {photo_share.id}")