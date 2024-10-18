from rest_framework import serializers
from collections import defaultdict
from .models import Schedule
from datetime import datetime
from .utils import is_time_overlap


class TimeSlotSerializer(serializers.Serializer):
    record_id = serializers.IntegerField()
    start = serializers.SerializerMethodField()
    stop = serializers.SerializerMethodField()
    ids = serializers.JSONField()

    def get_start(self, obj):
        return obj['start-time']

    def get_stop(self, obj):
        return obj['end-time']


class WeeklyScheduleSerializer(serializers.Serializer):
    schedule = serializers.SerializerMethodField()

    def get_schedule(self, obj):
        day_order = {
            'monday': 0,
            'tuesday': 1,
            'wednesday': 2,
            'thursday': 3,
            'friday': 4,
            'saturday': 5,
            'sunday': 6
        }

        weekly_schedule = defaultdict(list)

        for slot in obj:
            weekly_schedule[slot.day].append({
                "record_id": slot.id,
                "start-time": slot.start_time.strftime("%H:%M"),
                "end-time": slot.end_time.strftime("%H:%M"),
                "ids": slot.ids,
                "original_time": slot.start_time
            })

        sorted_schedule = sorted(weekly_schedule.items(), key=lambda x: day_order[x[0]])

        result = {}
        for day, slots in sorted_schedule:
            if slots:
                sorted_slots = sorted(slots, key=lambda x: x['original_time'])

                for slot in sorted_slots:
                    del slot['original_time']
                result[day] = TimeSlotSerializer(sorted_slots, many=True).data

        return result


class RecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = '__all__'


class EditRecordTimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['start_time', 'end_time']

    def validate(self, data):
        record_id = self.instance.id
        record_day = self.instance.day

        start = data.get('start_time')
        end = data.get('end_time')

        if isinstance(start, str):
            start = datetime.strptime(start, '%H:%M').time()
        if isinstance(end, str):
            end = datetime.strptime(end, '%H:%M').time()

        if not start:
            start = self.instance.start_time
        if not end:
            end = self.instance.end_time

        if start >= end:
            raise serializers.ValidationError("End time must be greater than start time.")

        existing_intervals = Schedule.objects.filter(day=record_day).exclude(id=record_id)

        for existing in existing_intervals:
            if is_time_overlap(start, end, existing.start_time, existing.end_time):
                raise serializers.ValidationError(f"Time interval {start} - {end} overlaps with an existing interval!")

        data['start_time'] = start
        data['end_time'] = end

        return data
