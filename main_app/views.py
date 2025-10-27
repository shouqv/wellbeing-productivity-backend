from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated ,IsAuthenticatedOrReadOnly
from .serializers import GoalSerializer , TaskSerializer , EmotionSerializer

from django.shortcuts import get_object_or_404
from .models import Goal , Task , Emotion
# Create your views here.

class GoalsIndex(APIView):
    # TODO - for now the permission is allow any to streamline testing apis
    permission_classes = [AllowAny]
    def get(self , request):
        try:
            # TODO - dont forget to uncomment the below once auth is done
            # queryset = Goal.objects.filter(user = request.user)
            queryset = Goal.objects.all()
            serializer = GoalSerializer(queryset , many = True)
            return Response(serializer.data, status = status.HTTP_200_OK)
        except Exception as error:
            return Response({'error': str(error)} , status = status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    # REMEMBER: the below is the post req needed
    # {
    #     "content": "to let the test succedd",
    #     "status": "active",
    #     "year": 2025,
    #     "user": 1
    # }

    def post(self, request):
        try:
            serializer = GoalSerializer(data=request.data)
            # TODO - check if the user id is automatically checked if it exist from the is_valid
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as error:
            return Response(
                {"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
            
class GoalDetail(APIView):
    # TODO - for now the permission is allow any to streamline testing apis
    permission_classes = [AllowAny]
    def put(self, request, goal_id):
        try:
            queryset = get_object_or_404(Goal, id=goal_id)
            serializer = GoalSerializer(queryset, data=request.data)
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as error:
            return Response(
                {"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 
            
    def delete(self, request, goal_id):
        try:
            queryset = get_object_or_404(Goal, id=goal_id)
            user_id = queryset.user.id
            queryset.delete()
            return Response(
                {"message": f"Goal {goal_id} has been deleted for user {user_id}"},
                status=status.HTTP_204_NO_CONTENT,
            )

        except Exception as error:
            return Response(
                {"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
            
            
class TasksIndex(APIView):
    # TODO - for now the permission is allow any to streamline testing apis
    permission_classes = [AllowAny]
    def get(self, request):
        try:
            # TODO - uncomment the bellow once auth is done
            # queryset = Task.objects.filter(user = request.user)
            queryset = Task.objects.all()
            # the below gets the query in http://127.0.0.1:8000/api/tasks?date=2025-10-25 for example
            date = request.query_params.get('date')

            if date:
                queryset = queryset.filter(date=date)
                
            serializer = TaskSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as error:
            return Response(
                {"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        #  {
        #         "id": 1,
        #         "content": "do front end",
        #         "date": "2025-10-27",
        #         "priority": 1,
        #         "status": "pending",
        #         "user": 1
        #     }

    def post(self, request):
        try:
            serializer = TaskSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as error:
            return Response(
                {"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TaskDetail(APIView):
    # TODO - for now the permission is allow any to streamline testing apis
    permission_classes = [AllowAny]
    def put(self, request, task_id):
        try:
            queryset = get_object_or_404(Task, id=task_id)
            serializer = TaskSerializer(queryset, data=request.data)
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as error:
            return Response(
                {"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 
    
    def delete(self, request, task_id):
        try:
            queryset = get_object_or_404(Task, id=task_id)
            user_id = queryset.user.id
            queryset.delete()
            return Response(
                {"message": f"Task {task_id} has been deleted for user {user_id}"},
                status=status.HTTP_204_NO_CONTENT,
            )

        except Exception as error:
            return Response(
                {"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )