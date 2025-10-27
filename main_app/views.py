from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated ,IsAuthenticatedOrReadOnly
from .serializers import GoalSerializer , TaskSerializer , EmotionSerializer
import ollama

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
            
            pending_tasks = queryset.filter(status='pending')
            in_progress_tasks = queryset.filter(status='in_progress' )
            completed_tasks = queryset.filter(status='completed' )
                
            serializer = TaskSerializer(queryset, many=True)
            return Response( {
                "message": f"Tasks",
                "pending_tasks": TaskSerializer(pending_tasks, many=True).data,
                "in_progress_tasks": TaskSerializer(in_progress_tasks, many=True).data,
                "completed_tasks": TaskSerializer(completed_tasks, many=True).data,
            }, status=status.HTTP_200_OK)

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






# crediting the local AI model from Ollama: https://ollama.com/ALIENTELLIGENCE/mentalwellness
def gen_response(user_input):
    response = ollama.chat(
        model="ALIENTELLIGENCE/mentalwellness",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are Luna, a mental wellness assistant. Always respond with one short, kind, supportive message. Never ask questions or continue the conversation. If a user expresses distress or thoughts of self-harm, gently remind them they are important and suggest reaching out for help — do not ask anything in return."
                )
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
    )

    return response['message']["content"]


# #    {
#         "id": 1,
#         "emoji": "😄",
#         "feeling_text": "im feeling great",
#         "ai_response": "wow good for you(that was from me dw its not AI response yet 😆)",
#         "date": "2025-10-27",
#         "user": 1
#     }
class EmotionIndex(APIView):
    # TODO - for now the permission is allow any to streamline testing apis
    permission_classes = [AllowAny]
    def get(self , request):
        try:
            # TODO - dont forget to uncomment the below once auth is done
            # TODO - decide whether the returned data is only 7 days, a week 
            # queryset = Emotion.objects.filter(user = request.user)
            queryset = Emotion.objects.all()
            serializer = EmotionSerializer(queryset , many = True)
            return Response(serializer.data, status = status.HTTP_200_OK)
        except Exception as error:
            return Response({'error': str(error)} , status = status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # TODO - update the entry later on with personlized previous data, so that 
    # the ai becomes smarter and understand the user state
    def post(self, request):
        try:
            data=request.data
            data['ai_response'] = gen_response(
            f"Today the user indicated their mood with emoji {data.get('emoji')} "
            f"and wrote this about their feelings: '{data.get('feeling_text')}'. "
            "Respond with a short, kind, supportive message."
            )
            serializer = EmotionSerializer(data = data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as error:
            return Response(
                {"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
            

class LinkTaskToGoal(APIView):
    permission_classes = [AllowAny]
    def patch(self, request, goal_id, task_id):
        goal = get_object_or_404(Goal, id=goal_id)
        task = get_object_or_404(Task, id=task_id)
        goal.tasks.add(task)
        
        goals_belong_to_task = Goal.objects.filter(tasks = task_id)
        goals_doesnot_belong_to_task = Goal.objects.exclude(tasks = task_id)
        
        return Response(
            {
                "message": f"You have linked the task {task_id} to the goal {goal_id}",
                "goals_belong_to_task": GoalSerializer(goals_belong_to_task, many=True).data,
                "goals_doesnot_belong_to_task": GoalSerializer(goals_doesnot_belong_to_task, many=True).data,
            },
            status=status.HTTP_200_OK,
        )
        
class UnlinkTaskFromGoal(APIView):
    permission_classes = [AllowAny]
    def patch(self, request, goal_id, task_id):
        # i might dont need to reltae the user id as the goal id and task id is unique to the user
        # user_id = request.data.get("user")
        goal = get_object_or_404(Goal, id=goal_id)
        task = get_object_or_404(Task, id=task_id)
        goal.tasks.remove(task)
        
        # goals_belong_to_task = Goal.objects.filter(tasks = task_id , user = user_id)
        # goals_doesnot_belong_to_task = Goal.objects.exclude(tasks = task_id).filter(user = user_id)
        
        goals_belong_to_task = Goal.objects.filter(tasks = task_id)
        goals_doesnot_belong_to_task = Goal.objects.exclude(tasks = task_id)
        
        return Response(
            {
                "message": f"You have unlinked the task {task_id} to the goal {goal_id}",
                "goals_belong_to_task": GoalSerializer(goals_belong_to_task, many=True).data,
                "goals_doesnot_belong_to_task": GoalSerializer(goals_doesnot_belong_to_task, many=True).data,
            },
            status=status.HTTP_200_OK,
        )