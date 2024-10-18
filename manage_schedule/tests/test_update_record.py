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


@pytest.fixture
def sample_schedule():
    return Schedule.objects.create(
        day='monday',
        start_time=time(9, 0),
        end_time=time(10, 0),
        ids=[1]
    )


@pytest.mark.django_db
class TestUpdateRecord:
    url = '/update-record/'

    def test_update_existing_record(self, authenticated_client, sample_schedule):
        """Test of updating an existing record"""
        new_data = {
            'start_time': '10:00',
            'end_time': '11:00'
        }
        response = authenticated_client.patch(f"{self.url}?record_id={sample_schedule.id}", data=new_data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['start_time'] == '10:00:00'
        assert response.data['end_time'] == '11:00:00'

        updated_record = Schedule.objects.get(id=sample_schedule.id)
        assert updated_record.start_time == time(10, 0)
        assert updated_record.end_time == time(11, 0)

    def test_update_nonexistent_record(self, authenticated_client):
        """Test for updating a non-existent record"""
        non_existent_id = 9999
        new_data = {
            'start_time': '10:00',
            'end_time': '11:00'
        }
        response = authenticated_client.patch(f"{self.url}?record_id={non_existent_id}", data=new_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data == 'The record with this timeline does not exist!'

    def test_update_with_invalid_data(self, authenticated_client, sample_schedule):
        """Update test with incorrect data"""
        invalid_data = {
            'start_time': '11:00',
            'end_time': '10:00'
        }
        response = authenticated_client.patch(f"{self.url}?record_id={sample_schedule.id}", data=invalid_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'End time must be greater than start time.' in str(response.data)

    def test_update_with_overlapping_time(self, authenticated_client, sample_schedule):
        """Update test with time overlapping with another record"""

        Schedule.objects.create(
            day='monday',
            start_time=time(11, 0),
            end_time=time(12, 0),
            ids=[2]
        )

        overlapping_data = {
            'start_time': '10:30',
            'end_time': '11:30'
        }
        response = authenticated_client.patch(f"{self.url}?record_id={sample_schedule.id}", data=overlapping_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Time interval 10:30:00 - 11:30:00 overlaps with an existing interval!' in str(response.data)

    def test_partial_update(self, authenticated_client, sample_schedule):
        """Partial update test (start_time only)"""
        partial_data = {
            'start_time': '09:30'
        }
        response = authenticated_client.patch(f"{self.url}?record_id={sample_schedule.id}", data=partial_data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['start_time'] == '09:30:00'
        assert response.data['end_time'] == '10:00:00'

    def test_unauthenticated_request(self, api_client, sample_schedule):
        """Access test without authentication"""
        new_data = {
            'start_time': '10:00',
            'end_time': '11:00'
        }
        response = api_client.patch(f"{self.url}?record_id={sample_schedule.id}", data=new_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_without_record_id(self, authenticated_client):
        """Update test without specifying record_id"""
        new_data = {
            'start_time': '10:00',
            'end_time': '11:00'
        }
        response = authenticated_client.patch(self.url, data=new_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data == 'The record with this timeline does not exist!'
