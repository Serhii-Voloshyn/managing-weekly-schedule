from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Schedule
from .serializers import WeeklyScheduleSerializer, RecordSerializer, EditRecordTimelineSerializer
from .utils import is_time_overlap
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class GetWeekSchedule(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        operation_description="Get the weekly schedule",
        responses={200: WeeklyScheduleSerializer(many=True)},
        tags=['Schedule']
    )
    def get(self, request):
        schedule = Schedule.objects.all()
        serialized = WeeklyScheduleSerializer(schedule)
        return Response(serialized.data, status=status.HTTP_200_OK)


class CreateRecord(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        data_format_example = {
            "day": "monday",
            "start_time": "12:15",
            "end_time": "13:00",
            "ids": [1, 2, 3, 4]
        }
        return Response(data_format_example, status=status.HTTP_200_OK)

    def post(self, request):
        user_data = request.data
        serializer = RecordSerializer(data=user_data)

        if serializer.is_valid():
            day = serializer.validated_data['day']
            new_start = serializer.validated_data['start_time']
            new_end = serializer.validated_data['end_time']

            existing_intervals = Schedule.objects.filter(day=day)

            for existing in existing_intervals:
                if is_time_overlap(new_start, new_end, existing.start_time, existing.end_time):
                    return Response(f"Time interval {new_start} - {new_end} overlaps with an existing interval!",
                                    status=status.HTTP_400_BAD_REQUEST)

            serializer.save()

            return Response('New record was added successfully!', status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteRecord(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        operation_description="Delete a record by its ID",
        manual_parameters=[
            openapi.Parameter(
                'record_id',
                openapi.IN_QUERY,
                description="ID of the record to delete",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: "The record was deleted successfully!",
            400: "Record ID is required to delete! Enter in correct format!",
            404: "This record already deleted or record with those timeline does not exist!"
        }
    )
    def delete(self, request):
        record_id = request.query_params.get('record_id')

        if not record_id:
            return Response('Record ID is required to delete! Enter in correct format!',
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            record = Schedule.objects.get(id=record_id)

            record.delete()

            return Response('The record was deleted successfully!',
                            status=status.HTTP_200_OK)

        except Schedule.DoesNotExist:
            return Response('This record already deleted or record with those timeline does not exist!',
                            status=status.HTTP_404_NOT_FOUND)


class UpdateRecord(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        operation_description="Update a record by its ID and new data",
        manual_parameters=[
            openapi.Parameter(
                'record_id',
                openapi.IN_QUERY,
                description="ID of the record to update",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        request_body=EditRecordTimelineSerializer,
        responses={
            200: EditRecordTimelineSerializer,
            400: "Bad request. Validation errors or invalid record data",
            404: "Record does not exist!"
        }
    )
    def patch(self, request):
        record_id = request.query_params.get('record_id')

        try:
            record = Schedule.objects.get(id=record_id)

        except Schedule.DoesNotExist:
            return Response('The record with this timeline does not exist!', status=status.HTTP_404_NOT_FOUND)

        serializer = EditRecordTimelineSerializer(record, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
