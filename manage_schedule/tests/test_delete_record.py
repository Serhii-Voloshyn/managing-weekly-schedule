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
class TestDeleteRecord:
    url = '/delete-record/'

    def test_delete_existing_record(self, authenticated_client, sample_schedule):
        """Test to delete an existing record"""
        response = authenticated_client.delete(f"{self.url}?record_id={sample_schedule.id}")

        assert response.status_code == status.HTTP_200_OK
        assert response.data == 'The record was deleted successfully!'
        assert not Schedule.objects.filter(id=sample_schedule.id).exists()

    def test_delete_nonexistent_record(self, authenticated_client):
        """Test for deleting a non-existent record"""
        non_existent_id = 9999
        response = authenticated_client.delete(f"{self.url}?record_id={non_existent_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data == 'This record already deleted or record with those timeline does not exist!'

    def test_delete_without_record_id(self, authenticated_client):
        """Test a delete attempt without specifying a record_id"""
        response = authenticated_client.delete(self.url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == 'Record ID is required to delete! Enter in correct format!'

    def test_unauthenticated_request(self, api_client):
        """Access test without authentication"""
        response = api_client.delete(f"{self.url}?record_id=1")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_invalid_record_id(self, authenticated_client):
        """Test with invalid record_id format"""
        response = authenticated_client.delete(f"{self.url}?record_id=99")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data == 'This record already deleted or record with those timeline does not exist!'
