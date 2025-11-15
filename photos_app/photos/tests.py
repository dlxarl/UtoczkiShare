from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Photo, PhotoShare
import os
from django.conf import settings

TEST_IMAGE_CONTENT = b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'

class PhotoAPITests(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='Password1')
        self.user2 = User.objects.create_user(username='user2', password='Password2')

        self.test_image = SimpleUploadedFile(
            name='test.gif',
            content=TEST_IMAGE_CONTENT,
            content_type='image/gif'
        )
        
        os.makedirs(settings.MEDIA_ROOT / 'uploads', exist_ok=True)
        
        # Note: This login() call might be redundant if using JWT tokens
        # self.client.login(username='user1', password='Password1')
        
        login_resp = self.client.post('/api/auth/login/', {'username': 'user1', 'password': 'Password1'})
        self.token1 = login_resp.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')

    def tearDown(self):
        for photo in Photo.objects.all():
            if photo.file and os.path.exists(photo.file.path):
                os.remove(photo.file.path)

    def _upload_photo(self, user, filename='test.gif'):
        """Helper function to upload a photo."""
        if user == self.user2:
            login_resp = self.client.post('/api/auth/login/', {'username': 'user2', 'password': 'Password2'})
            token2 = login_resp.data['access']
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token2}')
        else:
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
            
        image = SimpleUploadedFile(name=filename, content=TEST_IMAGE_CONTENT, content_type='image/gif')
        response = self.client.post('/api/photos/', {'file': image}, format='multipart')
        return response

    def test_photo_upload_authenticated(self):
        """
        Test that an authenticated user can upload a photo.
        """
        response = self._upload_photo(self.user1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Photo.objects.count(), 1)
        photo = Photo.objects.first()
        self.assertEqual(photo.owner, self.user1)
        self.assertEqual(photo.original_name, 'test.gif')

    def test_photo_upload_unauthenticated(self):
        """
        Test that an unauthenticated user cannot upload a photo.
        """
        self.client.credentials()
        response = self.client.post('/api/photos/', {'file': self.test_image}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_shows_only_own_photos(self):
        """
        [IDOR Test] Test that the list endpoint only shows the user's own photos.
        """

        self._upload_photo(self.user1, 'photo1.gif')
        
        self._upload_photo(self.user2, 'photo2.gif')
        
        self.assertEqual(Photo.objects.count(), 2)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        response = self.client.get('/api/photos/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['original_name'], 'photo1.gif')

    def test_get_other_user_photo_detail_forbidden(self):
        """
        [IDOR Test] Test that a user cannot retrieve details for another user's photo.
        """
        upload_resp = self._upload_photo(self.user2, 'photo2.gif')
        photo2_id = upload_resp.data['id']
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        response = self.client.get(f'/api/photos/{photo2_id}/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_share_own_photo_success(self):
        """
        Test that a user can successfully share their own photo.
        """
        upload_resp = self._upload_photo(self.user1)
        photo1_id = upload_resp.data['id']
        
        share_data = {
            'photo': photo1_id,
            'shared_to': self.user2.id
        }
        response = self.client.post('/api/photos/share/', share_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(PhotoShare.objects.filter(photo_id=photo1_id, shared_to=self.user2).exists())

    def test_share_other_user_photo_forbidden(self):
        """
        [IDOR Test] Test that a user is forbidden from sharing another user's photo.
        """
        upload_resp = self._upload_photo(self.user2)
        photo2_id = upload_resp.data['id']
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        share_data = {
            'photo': photo2_id,
            'shared_to': self.user1.id 
        }
        response = self.client.post('/api/photos/share/', share_data)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_protected_media_access_own_photo(self):
        """
        Test access to own photo file via the protected media endpoint.
        """
        upload_resp = self._upload_photo(self.user1)
        photo = Photo.objects.get(id=upload_resp.data['id'])
        
        response = self.client.get(f'/api/media/{photo.file.name}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, TEST_IMAGE_CONTENT)

    def test_protected_media_access_other_user_photo_forbidden(self):
        """
        [IDOR Test] Test that a user is forbidden from accessing another user's photo file.
        """
        upload_resp = self._upload_photo(self.user2)
        photo = Photo.objects.get(id=upload_resp.data['id'])
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        response = self.client.get(f'/api/media/{photo.file.name}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_protected_media_access_shared_photo(self):
        """
        Test that a user can access a photo file that has been shared with them.
        """
        upload_resp = self._upload_photo(self.user1)
        photo = Photo.objects.get(id=upload_resp.data['id'])
        
        PhotoShare.objects.create(photo=photo, shared_to=self.user2)
        
        login_resp = self.client.post('/api/auth/login/', {'username': 'user2', 'password': 'Password2'})
        token2 = login_resp.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token2}')
        
        response = self.client.get(f'/api/media/{photo.file.name}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, TEST_IMAGE_CONTENT)