from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Photo, PhotoShare
import os
from django.conf import settings

TEST_IMAGE_CONTENT = b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
TEST_TEXT_CONTENT = b'This is not an image.'

class PhotoAPITests(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='Password1', email='user1@example.com')
        self.user2 = User.objects.create_user(username='user2', password='Password2', email='user2@example.com')

        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        
        login_resp = self.client.post('/api/auth/login/', {'username': 'user1', 'password': 'Password1'})
        self.token1 = login_resp.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')

    def tearDown(self):
        for photo in Photo.objects.all():
            if photo.file and os.path.exists(photo.file.path):
                try:
                    os.remove(photo.file.path)
                except FileNotFoundError:
                    pass

    def _get_token(self, user, password):
        login_resp = self.client.post('/api/auth/login/', {'username': user, 'password': password})
        return login_resp.data['access']

    def _upload_photo(self, token, filename='test.gif', content=TEST_IMAGE_CONTENT, content_type='image/gif'):
        if not token:
            self.client.credentials()
        else:
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        image = SimpleUploadedFile(name=filename, content=content, content_type=content_type)
        response = self.client.post('/api/photos/', {'file': image}, format='multipart')
        return response

    def test_photo_upload_authenticated(self):
        response = self._upload_photo(self.token1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Photo.objects.count(), 1)
        photo = Photo.objects.first()
        self.assertEqual(photo.owner, self.user1)
        self.assertEqual(photo.original_name, 'test.gif')

    def test_photo_upload_unauthenticated(self):
        response = self._upload_photo(None, filename='test.gif')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_photo_upload_not_an_image(self):
        response = self._upload_photo(
            self.token1, 
            filename='test.txt', 
            content=TEST_TEXT_CONTENT, 
            content_type='text/plain'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Photo.objects.count(), 0)

    def test_photo_upload_xss_name(self):
        xss_name = "<script>alert(1)</script>.gif"
        response = self._upload_photo(self.token1, filename=xss_name)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        photo = Photo.objects.first()
        self.assertEqual(photo.original_name, xss_name)

    def test_list_shows_own_and_shared_photos(self):
        self._upload_photo(self.token1, 'photo1.gif')
        
        token2 = self._get_token('user2', 'Password2')
        upload_resp_user2 = self._upload_photo(token2, 'photo2.gif')
        
        photo2 = Photo.objects.get(id=upload_resp_user2.data['id'])
        PhotoShare.objects.create(photo=photo2, shared_to=self.user1)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        response = self.client.get('/api/photos/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        photo_names = {p['original_name'] for p in response.data}
        self.assertEqual(photo_names, {'photo1.gif', 'photo2.gif'})

    def test_list_shows_only_own_photos_no_shares(self):
        self._upload_photo(self.token1, 'photo1.gif')
        token2 = self._get_token('user2', 'Password2')
        self._upload_photo(token2, 'photo2.gif')
        self.assertEqual(Photo.objects.count(), 2)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        response = self.client.get('/api/photos/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['original_name'], 'photo1.gif')

    def test_get_other_user_photo_detail_forbidden(self):
        token2 = self._get_token('user2', 'Password2')
        upload_resp = self._upload_photo(token2, 'photo2.gif')
        photo2_id = upload_resp.data['id']
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        response = self.client.get(f'/api/photos/{photo2_id}/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_share_own_photo_success(self):
        upload_resp = self._upload_photo(self.token1)
        photo1_id = upload_resp.data['id']
        
        share_data = {
            'photo': photo1_id,
            'shared_to': self.user2.email
        }
        response = self.client.post('/api/photos/share/', share_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(PhotoShare.objects.filter(photo_id=photo1_id, shared_to=self.user2).exists())

    def test_share_photo_to_self_forbidden(self):
        upload_resp = self._upload_photo(self.token1)
        photo1_id = upload_resp.data['id']
        
        share_data = {
            'photo': photo1_id,
            'shared_to': self.user1.email
        }
        response = self.client.post('/api/photos/share/', share_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_share_photo_to_non_existent_email(self):
        upload_resp = self._upload_photo(self.token1)
        photo1_id = upload_resp.data['id']
        
        share_data = {
            'photo': photo1_id,
            'shared_to': 'ghost@example.com'
        }
        response = self.client.post('/api/photos/share/', share_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_share_other_user_photo_forbidden(self):
        token2 = self._get_token('user2', 'Password2')
        upload_resp = self._upload_photo(token2)
        photo2_id = upload_resp.data['id']
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        share_data = {
            'photo': photo2_id,
            'shared_to': self.user1.email 
        }
        response = self.client.post('/api/photos/share/', share_data)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_delete_own_photo(self):
        upload_resp = self._upload_photo(self.token1)
        photo1_id = upload_resp.data['id']
        self.assertEqual(Photo.objects.count(), 1)
        
        response = self.client.delete(f'/api/photos/{photo1_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Photo.objects.count(), 0)

    def test_user_cannot_delete_other_user_photo(self):
        token2 = self._get_token('user2', 'Password2')
        upload_resp = self._upload_photo(token2)
        photo2_id = upload_resp.data['id']
        self.assertEqual(Photo.objects.count(), 1)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        response = self.client.delete(f'/api/photos/{photo2_id}/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Photo.objects.count(), 1)

    def test_protected_media_access_own_photo(self):
        upload_resp = self._upload_photo(self.token1)
        photo = Photo.objects.get(id=upload_resp.data['id'])
        
        response = self.client.get(f'/api/media/{photo.file.name}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, TEST_IMAGE_CONTENT)

    def test_protected_media_access_other_user_photo_forbidden(self):
        token2 = self._get_token('user2', 'Password2')
        upload_resp = self._upload_photo(token2)
        photo = Photo.objects.get(id=upload_resp.data['id'])
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        response = self.client.get(f'/api/media/{photo.file.name}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_protected_media_access_shared_photo(self):
        upload_resp = self._upload_photo(self.token1)
        photo = Photo.objects.get(id=upload_resp.data['id'])
        
        PhotoShare.objects.create(photo=photo, shared_to=self.user2)
        
        token2 = self._get_token('user2', 'Password2')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token2}')
        
        response = self.client.get(f'/api/media/{photo.file.name}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, TEST_IMAGE_CONTENT)