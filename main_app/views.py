from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
import re
from .serializers import GoalSerializer , TaskSerializer , EmotionSerializer , VisionBoardSerializer
import ollama
from datetime import date

from django.contrib.auth import get_user_model
User = get_user_model()

from django.shortcuts import get_object_or_404
from .models import Goal , Task , Emotion , VisionBoard
# Create your views here.

class GoalsIndex(APIView):
    # TODO - for now the permission is allow any to streamline testing apis
    # TODO - maybe provide the goals for a specific year only
    permission_classes = [IsAuthenticated]
    def get(self , request):
        try:
            # TODO - dont forget to uncomment the below once auth is done
            queryset = Goal.objects.filter(user = request.user)
            # queryset = Goal.objects.all()
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
                # serializer.save()
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as error:
            return Response(
                {"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
            
class GoalDetail(APIView):
    # TODO - for now the permission is allow any to streamline testing apis
    permission_classes = [IsAuthenticated] 
    def get(self , request, goal_id):
        try:
            queryset = get_object_or_404(Goal, id=goal_id, user=request.user)
            serializer = GoalSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as error:
            return Response(
                {"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    def put(self, request, goal_id):
        try:
            queryset = get_object_or_404(Goal, id=goal_id, user=request.user)
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
            queryset = get_object_or_404(Goal, id=goal_id, user=request.user)
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
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            
            queryset = Task.objects.filter(user = request.user)
            # queryset = Task.objects.all()
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
                # serializer.save()
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as error:
            return Response(
                {"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TaskDetail(APIView):
    # TODO - for now the permission is allow any to streamline testing apis
    permission_classes = [IsAuthenticated] 
    def get(self , request, task_id):
        try:
            queryset = get_object_or_404(Task, id=task_id, user=request.user)
            serializer = TaskSerializer(queryset)
            
            
            # goals_belong_to_task = Goal.objects.filter(task=task_id , user=request.user)
            goals_belong_to_task = queryset.goals.all()
            goals_doesnot_belong_to_task = Goal.objects.filter(user=request.user).exclude(id__in=queryset.goals.all().values_list("id"))
            
            data = serializer.data
            data["goals_belong_to_task"] = GoalSerializer(goals_belong_to_task, many=True).data
            data["goals_doesnot_belong_to_task"] = GoalSerializer(goals_doesnot_belong_to_task, many=True).data
            
            return Response(data, status=status.HTTP_200_OK)
        except Exception as error:
            return Response(
                {"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    def put(self, request, task_id):
        try:
            queryset = get_object_or_404(Task, id=task_id, user=request.user)
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
            queryset = get_object_or_404(Task, id=task_id, user=request.user)
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
    permission_classes = [IsAuthenticated]
    def get(self , request):
        try:
            
            # TODO - decide whether the returned data is only 7 days, a week 
            queryset = Emotion.objects.filter(user = request.user)
            # queryset = Emotion.objects.all()
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
                # serializer.save()
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as error:
            return Response(
                {"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
            

# class LinkTaskToGoal(APIView):
#     permission_classes = [AllowAny]
#     def patch(self, request, goal_id, task_id):
#         goal = get_object_or_404(Goal, id=goal_id)
#         task = get_object_or_404(Task, id=task_id)
#         goal.tasks.add(task)
        
#         goals_belong_to_task = Goal.objects.filter(tasks = task_id)
#         goals_doesnot_belong_to_task = Goal.objects.exclude(tasks = task_id)
        
#         return Response(
#             {
#                 "message": f"You have linked the task {task_id} to the goal {goal_id}",
#                 "goals_belong_to_task": GoalSerializer(goals_belong_to_task, many=True).data,
#                 "goals_doesnot_belong_to_task": GoalSerializer(goals_doesnot_belong_to_task, many=True).data,
#             },
#             status=status.HTTP_200_OK,
#         )

# class UnlinkTaskFromGoal(APIView):
#     permission_classes = [AllowAny]
#     def patch(self, request, goal_id, task_id):
#         # i might dont need to reltae the user id as the goal id and task id is unique to the user
#         # user_id = request.data.get("user")
#         goal = get_object_or_404(Goal, id=goal_id)
#         task = get_object_or_404(Task, id=task_id)
#         goal.tasks.remove(task)
        
#         # goals_belong_to_task = Goal.objects.filter(tasks = task_id , user = user_id)
#         # goals_doesnot_belong_to_task = Goal.objects.exclude(tasks = task_id).filter(user = user_id)
        
#         goals_belong_to_task = Goal.objects.filter(tasks = task_id)
#         goals_doesnot_belong_to_task = Goal.objects.exclude(tasks = task_id)
        
#         return Response(
#             {
#                 "message": f"You have unlinked the task {task_id} to the goal {goal_id}",
#                 "goals_belong_to_task": GoalSerializer(goals_belong_to_task, many=True).data,
#                 "goals_doesnot_belong_to_task": GoalSerializer(goals_doesnot_belong_to_task, many=True).data,
#             },
#             status=status.HTTP_200_OK,
#         )
        

class LinkGoalToTask(APIView):
    permission_classes = [IsAuthenticated] 
    def patch(self, request, goal_id, task_id):
        goal = get_object_or_404(Goal, id=goal_id, user=request.user)
        task = get_object_or_404(Task, id=task_id, user=request.user)
        task.goals.add(goal)
        
        # goals_belong_to_task = Goal.objects.filter(task=task_id)
        # goals_doesnot_belong_to_task = Goal.objects.exclude(
        #     id__in=task.goals.all().values_list("id")
        # )
        
        goals_belong_to_task = task.goals.all()
        goals_doesnot_belong_to_task = Goal.objects.filter(user=request.user).exclude(id__in=task.goals.all().values_list("id"))

        return Response(
            {
                "message": f"You have linked the task {task_id} to the goal {goal_id}",
                "goals_belong_to_task": GoalSerializer(goals_belong_to_task, many=True).data,
                "goals_doesnot_belong_to_task": GoalSerializer(goals_doesnot_belong_to_task, many=True).data,
            },
            status=status.HTTP_200_OK,
        )

class UnLinkGoalToTask(APIView):
    permission_classes = [IsAuthenticated] 
    def patch(self, request, goal_id, task_id):
        goal = get_object_or_404(Goal, id=goal_id, user=request.user)
        task = get_object_or_404(Task, id=task_id, user=request.user)
        task.goals.remove(goal)
        
        # goals_belong_to_task = Goal.objects.filter(task=task_id)
        # goals_doesnot_belong_to_task = Goal.objects.exclude(
        #     id__in=task.goals.all().values_list("id")
        # )
        
        goals_belong_to_task = task.goals.all()
        goals_doesnot_belong_to_task = Goal.objects.filter(user=request.user).exclude(id__in=task.goals.all().values_list("id"))

        return Response(
            {
                "message": f"You have unlinked the task {task_id} to the goal {goal_id}",
                "goals_belong_to_task": GoalSerializer(goals_belong_to_task, many=True).data,
                "goals_doesnot_belong_to_task": GoalSerializer(goals_doesnot_belong_to_task, many=True).data,
            },
            status=status.HTTP_200_OK,
        )


        
class CheckTodayEmotionSubmission(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        has_entry = Emotion.objects.filter(user=request.user, date=date.today()).exists()
        # has_entry = Emotion.objects.filter( date=date.today()).exists()
        if has_entry:
            # might need to delte last, cus either way they only will have one entry per day
            emotion = Emotion.objects.filter(user=request.user, date=date.today()).last()
            serialized = EmotionSerializer(emotion).data
            return Response({
                "already_submitted": True,
                **serialized  
            })
        return Response({"already_submitted": has_entry})
    
    
# TODO 
# in the dashboard retrun the number of tasks per each goal


class VisionBoard(APIView):
    permission_classes = [IsAuthenticated] 

    def get(self, request):
        try:
            board = VisionBoard.objects.get(user=request.user)
            serializer = VisionBoardSerializer(board)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except VisionBoard.DoesNotExist:
            return Response({'tldraw_data': {}}, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({'error': str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = VisionBoardSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({'error': str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        try:
            board, created = VisionBoard.objects.get_or_create(user=request.user)
            board.tldraw_data = request.data.get('tldraw_data', {})
            board.save()
            return Response({'message': 'Vision board updated successfully.'}, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({'error': str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Crediting https://git.generalassemb.ly/SDA-SEB-02-V/DRF-example/blob/main/cat-collector-backend/main_app/views.py#L252-L279
class SignupUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        if not username or not password or not email:
            return Response(
                {"error": "Please provide a username, password, and email"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if User.objects.filter(username=username).exists():
            return Response(
                {'error': "User Already Exisits"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
            
        if len(password) < 8:
            return Response({"error": "Password must be at least 8 characters long"}, status=status.HTTP_400_BAD_REQUEST)
        if not re.search(r"[A-Z]", password):
            return Response({"error": "Password must contain at least one uppercase letter"}, status=status.HTTP_400_BAD_REQUEST)
        if not re.search(r"[a-z]", password):
            return Response({"error": "Password must contain at least one lowercase letter"}, status=status.HTTP_400_BAD_REQUEST)
        if not re.search(r"[0-9]", password):
            return Response({"error": "Password must contain at least one number"}, status=status.HTTP_400_BAD_REQUEST)
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return Response({"error": "Password must contain at least one special character"}, status=status.HTTP_400_BAD_REQUEST)
            
            

        user = User.objects.create_user(
            username=username, email=email, password=password
        )
        
        return Response(
            {"id": user.id, "username": user.username, "email": user.email},
            status=status.HTTP_201_CREATED,
        )