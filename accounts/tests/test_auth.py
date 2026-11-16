from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from accounts.models import User

class RegisterTestCase(APITestCase):

    def test_register_user(self):
        url = reverse('register')
        data = {
            'username': 'TestUser',
            'email': 'test@example.com',
            'first_name': 'test',
            'last_name': 'user',
            'password': 'StrongPass123',

        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='TestUser')
        self.assertEqual(user.role , User.Role.CUSTOMER)
        self.assertTrue(user.check_password(data['password']))

    def test_me_requires_authentication(self):
        url = reverse('me')

        response = self.client.get(url)

        self.assertEqual(response.status_code , status.HTTP_401_UNAUTHORIZED)

    def test_me_return_user_data(self):
        user = User.objects.create_user(username='meuser',email='hi@gmail.com',password='salam')

        self.client.force_authenticate(user=user)

        url = reverse('me')
        response = self.client.get(url)

        self.assertEqual(response.status_code , status.HTTP_200_OK)
        self.assertEqual(response.data['username'],user.username)
        self.assertEqual(response.data['email'],user.email)

    def test_login_return_jwt_token(self):
        User.objects.create_user(username='testuser',email='hello@gmail.com',password='asdf')
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'asdf'
        }
        response = self.client.post(url,data)
        self.assertEqual(response.status_code , status.HTTP_200_OK)
        self.assertIn('access',response.data)
        self.assertIn('refresh',response.data)
