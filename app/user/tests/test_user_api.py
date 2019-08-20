from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient


CREATE_USER_URL = reverse('user:create')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUsersApiTests(TestCase):
    """
    Test public (unauthenticated) requests to the user endpoints
    """

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """
        User should be created when valid payload is provided
        """
        payload = {
            'name': 'Testy McTest',
            'email': 'test@example.com',
            'password': 'testpass',
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_duplicate_user_failure(self):
        """
        User creation should fail when duplicate user exists
        """
        payload = {'email': 'test@example.com', 'password': 'testpass'}

        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_length_failure(self):
        """
        User creation should fail when a password of insufficient length is
        provided
        """
        payload = {'email': 'test@example.com', 'password': 'pw'}

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(email=payload['email'])
        self.assertFalse(user_exists)