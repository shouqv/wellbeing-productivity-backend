from django.urls import path
from .views import GoalsIndex , GoalDetail , TasksIndex ,TaskDetail , EmotionIndex , LinkTaskToGoal , UnlinkTaskFromGoal
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
path('goals/', GoalsIndex.as_view(), name='goal_index'),
path('goals/<int:goal_id>/', GoalDetail.as_view(), name='goal_detail'),
path('tasks/', TasksIndex.as_view(), name='task_index'),
path('tasks/<int:task_id>/', TaskDetail.as_view(), name='task_detail'),
path('emotions/', EmotionIndex.as_view(), name='emotion_detail'),
path('goals/<int:goal_id>/link-task/<int:task_id>/', LinkTaskToGoal.as_view(), name='link_task_to_goal'),
path('goals/<int:goal_id>/unlink-task/<int:task_id>/', UnlinkTaskFromGoal.as_view(), name='unlink_task_from_goal'),
]