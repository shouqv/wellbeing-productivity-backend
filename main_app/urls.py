from django.urls import path
from .views import GoalsIndex , GoalDetail , TasksIndex ,TaskDetail , EmotionIndex , LinkGoalToTask , UnLinkGoalToTask, CheckTodayEmotionSubmission ,SignupUserView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
path('goals/', GoalsIndex.as_view(), name='goal_index'),
path('goals/<int:goal_id>/', GoalDetail.as_view(), name='goal_detail'),
path('tasks/', TasksIndex.as_view(), name='task_index'),
path('tasks/<int:task_id>/', TaskDetail.as_view(), name='task_detail'),
path('emotions/', EmotionIndex.as_view(), name='emotion_detail'),
path('emotions/check/', CheckTodayEmotionSubmission.as_view(), name='check_emotion_submission'),
path('tasks/<int:task_id>/link-goal/<int:goal_id>/', LinkGoalToTask.as_view(), name='link_goal_to_task'),
path('tasks/<int:task_id>/unlink-goal/<int:goal_id>/', UnLinkGoalToTask.as_view(), name='link_goal_to_task'),

path('login/', TokenObtainPairView.as_view(), name='login'),
path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
path('signup/', SignupUserView.as_view(), name='signup')

]