from django.urls import path
from .views import GoalsIndex , GoalDetail
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
path('goals/', GoalsIndex.as_view(), name='goal_index'),
path('goals/<int:goal_id>/', GoalDetail.as_view(), name='goal_detail'),
]