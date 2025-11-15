from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status

class UserAuthTests(APITestCase):

    def test_user_registration_success(self):
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'StrongPassword123'
        }
        response = self.client.post('/api/auth/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        self.assertTrue(User.objects.filter(username='testuser').exists())
        user = User.objects.get(username='testuser')
        
        self.assertNotEqual(user.password, 'StrongPassword123')
        self.assertTrue(user.check_password('StrongPassword123'))

    def test_user_registration_duplicate_username(self):
        User.objects.create_user(username='testuser', password='Password1')
        
        data = {
            'username': 'testuser',
            'email': 'another@example.com',
            'password': 'StrongPassword123'
        }
        response = self.client.post('/api/auth/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_success(self):
        User.objects.create_user(username='loginuser', password='LoginPassword123')
        
        data = {
            'username': 'loginuser',
            'password': 'LoginPassword123'
        }
        response = self.client.post('/api/auth/login/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_login_invalid_credentials(self):
        User.objects.create_user(username='loginuser', password='LoginPassword123')
        
        data = {
            'username': 'loginuser',
            'password': 'WrongPassword'
        }
        response = self.client.post('/api/auth/login/', data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)