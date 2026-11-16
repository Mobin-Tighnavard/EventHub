from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from accounts.models import User


class EventPermissionTestCase(APITestCase):

    def test_customer_cannot_create_event(self):
        user = User.objects.create_user(username='john',
                                        email='john@gmail.com',
                                        password='asdf',
                                        role = User.Role.CUSTOMER
                                        )
        self.client.force_authenticate(user=user)

        url = reverse('event-create')

        response = self.client.post(url,{})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)