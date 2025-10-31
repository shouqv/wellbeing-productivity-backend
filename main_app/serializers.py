from rest_framework import serializers
from .models import Goal,Task , Emotion , VisionBoard




class EmotionSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model=Emotion
        fields = "__all__"


class GoalSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model=Goal
        fields = "__all__"
        
        
class TaskSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    goals = GoalSerializer(many=True, read_only=True)
    class Meta:
        model=Task
        fields = "__all__"
        
        
class VisionBoardSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = VisionBoard
        fields = ["tldraw_data"]
