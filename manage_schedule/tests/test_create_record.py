import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from datetime import time
from manage_schedule.models import Schedule


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticated_client(api_client):
    user = User.objects.create_user(username='tester12345', password='testpass123')
    api_client.force_authenticate(user=user)
    return api_client


@pytest.mark.django_db
class TestCreateRecord:
    def test_successful_record_creation(self, authenticated_client):
        data = {
            'day': 'monday',
            'start_time': '09:05',
            'end_time': '10:05',
            'ids': [1, 2]
        }

        url = '/create-record/'

        response = authenticated_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data == 'New record was added successfully!'

        assert Schedule.objects.count() == 1
        schedule = Schedule.objects.first()
        assert schedule.day == 'monday'
        assert schedule.start_time == time(9, 5)
        assert schedule.end_time == time(10, 5)
        assert schedule.ids == [1, 2]

    def test_overlapping_time_intervals(self, authenticated_client):

        Schedule.objects.create(
            day='monday',
            start_time=time(9, 0),
            end_time=time(10, 0),
            ids=[1]
        )

        data = {
            'day': 'monday',
            'start_time': '09:30',
            'end_time': '10:30',
            'ids': [2]
        }

        url = '/create-record/'
        response = authenticated_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "overlaps with an existing interval" in response.data

    def test_unauthenticated_request(self, api_client):
        data = {
            'day': 'monday',
            'start_time': '09:00',
            'end_time': '10:00',
            'ids': [1]
        }

        url = '/create-record/'
        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_invalid_data(self, authenticated_client):
        data = {
            'day': 'monday',
            'start_time': 'invalid_time',
            'end_time': '10:00',
            'ids': [1]
        }

        url = '/create-record/'
        response = authenticated_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
