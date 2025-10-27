from rest_framework import serializers
from .models import Goal,Task , Emotion

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model=Task
        fields = "__all__"


class EmotionSerializer(serializers.ModelSerializer):
    class Meta:
        model=Emotion
        fields = "__all__"


class GoalSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)
    class Meta:
        model=Goal
        fields = "__all__"
