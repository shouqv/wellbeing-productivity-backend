from django.urls import path
from .views import GoalsIndex , GoalDetail , TasksIndex ,TaskDetail , EmotionIndex
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
path('goals/', GoalsIndex.as_view(), name='goal_index'),
path('goals/<int:goal_id>/', GoalDetail.as_view(), name='goal_detail'),
path('tasks/', TasksIndex.as_view(), name='task_index'),
path('tasks/<int:task_id>/', TaskDetail.as_view(), name='task_detail'),
path('emotions/', EmotionIndex.as_view(), name='emotion_detail'),
]