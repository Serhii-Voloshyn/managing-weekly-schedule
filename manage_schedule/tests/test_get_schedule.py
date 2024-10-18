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
    schedules = [
        Schedule.objects.create(
            day='monday',
            start_time=time(9, 0),
            end_time=time(10, 0),
            ids=[1]
        ),
        Schedule.objects.create(
            day='monday',
            start_time=time(11, 0),
            end_time=time(12, 0),
            ids=[2]
        ),
        Schedule.objects.create(
            day='tuesday',
            start_time=time(14, 0),
            end_time=time(15, 0),
            ids=[3]
        )
    ]
    return schedules


@pytest.mark.django_db
class TestGetWeekSchedule:
    url = '/weekly-schedule/'

    def test_get_empty_schedule(self, authenticated_client):
        """Test for obtaining an empty schedule"""
        response = authenticated_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {'schedule': {}}

    def test_get_populated_schedule(self, authenticated_client, sample_schedule):
        """Test of getting a schedule with data"""
        response = authenticated_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK

        assert 'schedule' in response.data
        schedule_data = response.data['schedule']

        assert 'monday' in schedule_data
        assert 'tuesday' in schedule_data

        monday_slots = schedule_data['monday']
        assert len(monday_slots) == 2

        first_slot = monday_slots[0]
        assert 'record_id' in first_slot
        assert 'start' in first_slot
        assert 'stop' in first_slot
        assert 'ids' in first_slot

        assert first_slot['start'] == '09:00'
        assert first_slot['stop'] == '10:00'

    def test_schedule_sorting(self, authenticated_client, sample_schedule):
        """Schedule sorting test"""

        Schedule.objects.create(
            day='monday',
            start_time=time(8, 0),
            end_time=time(9, 0),
            ids=[4]
        )

        response = authenticated_client.get(self.url)

        monday_slots = response.data['schedule']['monday']

        assert monday_slots[0]['start'] == '08:00'
        assert monday_slots[1]['start'] == '09:00'
        assert monday_slots[2]['start'] == '11:00'

    def test_unauthenticated_request(self, api_client):
        """Access test without authentication"""
        response = api_client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_day_ordering(self, authenticated_client, sample_schedule):
        """Test of the order of the days of the week"""

        Schedule.objects.create(day='wednesday', start_time=time(9, 0), end_time=time(10, 0), ids=[5])
        Schedule.objects.create(day='friday', start_time=time(9, 0), end_time=time(10, 0), ids=[6])

        response = authenticated_client.get(self.url)
        schedule_data = response.data['schedule']

        days = list(schedule_data.keys())

        if 'monday' in days and 'tuesday' in days:
            assert days.index('monday') < days.index('tuesday')
        if 'tuesday' in days and 'wednesday' in days:
            assert days.index('tuesday') < days.index('wednesday')
        if 'wednesday' in days and 'friday' in days:
            assert days.index('wednesday') < days.index('friday')

    def test_empty_day_exclusion(self, authenticated_client, sample_schedule):
        """Test that empty days are not included in the response"""
        response = authenticated_client.get(self.url)
        schedule_data = response.data['schedule']

        assert 'sunday' not in schedule_data
        assert 'saturday' not in schedule_data
