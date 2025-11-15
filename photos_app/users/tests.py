from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status

class UserAuthTests(APITestCase):

    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'StrongPassword123',
            'password_confirm': 'StrongPassword123'
        }

    def test_user_registration_success(self):
        response = self.client.post('/api/auth/register/', self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())
        user = User.objects.get(username='testuser')
        self.assertNotEqual(user.password, 'StrongPassword123')
        self.assertTrue(user.check_password('StrongPassword123'))

    def test_user_registration_duplicate_username(self):
        User.objects.create_user(username='testuser', password='Password1', email='another@example.com')
        response = self.client.post('/api/auth/register/', self.user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_user_registration_duplicate_email(self):
        User.objects.create_user(username='anotheruser', password='Password1', email='test@example.com')
        response = self.client.post('/api/auth/register/', self.user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_user_registration_password_mismatch(self):
        data = self.user_data.copy()
        data['password_confirm'] = 'WrongConfirm123'
        response = self.client.post('/api/auth/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_user_registration_password_too_short(self):
        data = self.user_data.copy()
        data['password'] = 'short'
        data['password_confirm'] = 'short'
        response = self.client.post('/api/auth/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_user_registration_password_is_username(self):
        data = self.user_data.copy()
        data['username'] = 'testuser'
        data['password'] = 'testuser'
        data['password_confirm'] = 'testuser'
        response = self.client.post('/api/auth/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_user_login_success(self):
        User.objects.create_user(username='loginuser', password='LoginPassword123')
        data = {'username': 'loginuser', 'password': 'LoginPassword123'}
        response = self.client.post('/api/auth/login/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_login_invalid_credentials(self):
        User.objects.create_user(username='loginuser', password='LoginPassword123')
        data = {'username': 'loginuser', 'password': 'WrongPassword'}
        response = self.client.post('/api/auth/login/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)