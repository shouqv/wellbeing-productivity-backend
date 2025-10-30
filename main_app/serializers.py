from rest_framework import serializers
from .models import Goal,Task , Emotion




class EmotionSerializer(serializers.ModelSerializer):
    class Meta:
        model=Emotion
        fields = "__all__"


class GoalSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Goal
        fields = "__all__"
        
        
class TaskSerializer(serializers.ModelSerializer):
    goals = GoalSerializer(many=True, read_only=True)
    class Meta:
        model=Task
        fields = "__all__"
