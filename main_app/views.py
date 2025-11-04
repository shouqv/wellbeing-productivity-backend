from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
import re
from .serializers import GoalSerializer , TaskSerializer , EmotionSerializer , VisionBoardSerializer , AiAnalysisReportSerilaizer
import ollama
from datetime import date , timedelta


from django.contrib.auth import get_user_model
User = get_user_model()

from django.shortcuts import get_object_or_404
from .models import Goal , Task , Emotion , VisionBoard , AiAnalysisReport


class GoalsIndex(APIView):
    permission_classes = [IsAuthenticated]
    def get(self , request):
        try:
            queryset = Goal.objects.filter(user = request.user)
            serializer = GoalSerializer(queryset , many = True)
            return Response(serializer.data, status = status.HTTP_200_OK)
        except Exception as error:
            return Response({'error': str(error)} , status = status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    

    def post(self, request):
        try:
            serializer = GoalSerializer(data=request.data)
            if serializer.is_valid():

                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as error:
            return Response(
                {"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
            
class GoalDetail(APIView):
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
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            
            queryset = Task.objects.filter(user = request.user)
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
        

    def post(self, request):
        try:
            serializer = TaskSerializer(data=request.data)
            if serializer.is_valid():

                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as error:
            return Response(
                {"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TaskDetail(APIView):

    permission_classes = [IsAuthenticated] 
    def get(self , request, task_id):
        try:
            queryset = get_object_or_404(Task, id=task_id, user=request.user)
            serializer = TaskSerializer(queryset)
            
            
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
            }, 
            
        ]
        , keep_alive=False
    )

    return response['message']["content"]



class EmotionIndex(APIView):
    permission_classes = [IsAuthenticated]
    def get(self , request):
        try:
            
            queryset = Emotion.objects.filter(user = request.user)
            serializer = EmotionSerializer(queryset , many = True)
            return Response(serializer.data, status = status.HTTP_200_OK)
        except Exception as error:
            return Response({'error': str(error)} , status = status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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
                serializer.save(user=request.user)
                
                try:
                    ai_report = AiAnalysisReport.objects.filter(user=request.user, date=date.today()).order_by('-time_reported').first()
                    ai_report.save()  
                except Exception:
                    pass
                    
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as error:
            return Response(
                {"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
            



class LinkGoalToTask(APIView):
    permission_classes = [IsAuthenticated] 
    def patch(self, request, goal_id, task_id):
        goal = get_object_or_404(Goal, id=goal_id, user=request.user)
        task = get_object_or_404(Task, id=task_id, user=request.user)
        task.goals.add(goal)
        
        
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

        if has_entry:
            emotion = Emotion.objects.filter(user=request.user, date=date.today()).last()
            serialized = EmotionSerializer(emotion).data
            return Response({
                "already_submitted": True,
                **serialized  
            })
        return Response({"already_submitted": has_entry})
    
    



class VisionBoardDetial(APIView):
    permission_classes = [IsAuthenticated] 

    def get(self, request):
        try:
            board, created = VisionBoard.objects.get_or_create(user=request.user)
            serializer = VisionBoardSerializer(board)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({'error': str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        try:
            board = get_object_or_404(VisionBoard , user=request.user)
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
        
        if User.objects.filter(username__iexact=username).exists():
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



def gen_dashboard_summary(user_data):
    weekly_tasks_data = user_data.get("tasks", [])
    weekly_emotions_data = user_data.get("emotions", [])
    
    emotions_by_date = {e['date']: e for e in weekly_emotions_data}
    tasks_by_date= {}
    for task in weekly_tasks_data:
        task_date = task['date']
        if task_date not in tasks_by_date:
            tasks_by_date[task_date] = []
        tasks_by_date[task_date].append(task)

    
    all_dates = sorted(set(emotions_by_date.keys()) | set(tasks_by_date.keys()))

    summary_text = "Here is the user's mood data (do not infer missing days):\n"

    for day_date in all_dates:
        emotion_entry = emotions_by_date.get(day_date, {})
        emoji = emotion_entry.get("emoji", "None")
        feeling_text = emotion_entry.get("feeling_text", "")

        summary_text += f"\n{day_date} (Mood: {emoji}, Journal: {feeling_text}):\n"


        day_tasks = tasks_by_date.get(day_date, [])
        if day_tasks:
            for t in day_tasks:
                summary_text += f"  - Task '{t['content']}' is {t['status']}\n"
        else:
            summary_text += "  - No tasks for this day.\n"
    print(summary_text)

    system_prompt = (
     "You are Luna, a kind and supportive mental wellness assistant. "
    "Speak directly to the user using 'you' and 'your' instead of 'the user'. "
    "Analyze ONLY the mood and task data provided below — do not imagine or infer missing days. "
    "Write exactly two short sentences: "
    "the first should describe the emotional trend you observed, addressing the user directly; "
    "the second should give a gentle coping or self-care suggestion. "
    "Avoid prefacing with phrases like 'Here's a summary' or 'Based on the provided data' — just speak naturally.")
    
    response = ollama.chat(
        model="ALIENTELLIGENCE/mentalwellness",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": summary_text}
        ] ,  keep_alive=False
    )
    
    return response['message']["content"] if response['message'] else "No summary available."


class DashBoardInfo(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            user = request.user
            today = date.today()
            
            
            # - get coompleted tasks out of all tasks:
            all_tasks = Task.objects.filter(user=user , date=today)
            total_tasks = all_tasks.count()
            completed_tasks_count = all_tasks.filter(status='completed').count()
            
            
            # - returning the week emotion + tasks info entry to be sent to the ai
            #   crediting https://stackoverflow.com/questions/17016051/need-sunday-as-the-first-day-of-the-week
            days_since_sunday = (today.weekday() + 1) % 7
            
            #   crediting https://www.dataquest.io/blog/python-datetime/
            #   the below retrieves the date of the sunday of the current week
            start_of_week = today - timedelta(days=days_since_sunday)
            

            weekly_tasks = Task.objects.filter(user=user, date__gte=start_of_week, date__lte=today)
            weekly_tasks_data = TaskSerializer(weekly_tasks, many=True).data

            weekly_emotions = Emotion.objects.filter(
                user=user,
                date__gte=start_of_week,
                date__lte=today
            ).order_by('date')

            weekly_emotions_data = EmotionSerializer(weekly_emotions, many=True).data
            
            user_data_for_ai = {
            "tasks": weekly_tasks_data,       
            "emotions": weekly_emotions_data  
            }
            #   below checkes/create basec on if there is already a generatred response or not            
            ai_report = check_get_ai_submitted_report(user , today)
            if not ai_report:
                ai_analytics = gen_dashboard_summary(user_data_for_ai)
                data={ 'ai_report': ai_analytics , 'date': today}
                serializer = AiAnalysisReportSerilaizer(data = data)
                if serializer.is_valid():
                    serializer.save(user=user)
            else:
                 ai_analytics = ai_report
                

            # emojis for this month
            start_of_month = today.replace(day=1)
            monthly_emotions = Emotion.objects.filter(
                user=user,
                date__gte=start_of_month,
                date__lte=today
            )
            monthly_emotions_data = EmotionSerializer(monthly_emotions , many=True).data
            emojis_this_month = monthly_emotions.values_list('emoji', flat=True)


            # for each goal number of linked tasks and completed tasks
            goals = Goal.objects.filter(user=user)
            goal_info = []
            for goal in goals:
                linked_tasks = Task.objects.filter(user=user, goals = goal.id)
                completed_linked_tasks = linked_tasks.filter(status='completed')
                goal_info.append({
                    "goal_id": goal.id,
                    "goal_content": goal.content,
                    "linked_tasks_count": linked_tasks.count(),
                    "completed_linked_tasks_count": completed_linked_tasks.count(),
                    "status": goal.status
                })

            # high priority tasks
            high_priority_tasks = all_tasks.filter(priority=3).order_by('-status')
            high_priority_tasks_data = TaskSerializer(high_priority_tasks, many=True).data

            # any achieved goal 
            achieved_goals = goals.filter(status='achieved')

            # each emoji and number of occurance in this month 
            emoji_counts = {}
            for emoji in emojis_this_month:
                emoji_counts[emoji] = emoji_counts.get(emoji, 0) + 1
                
            response_data = {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks_count,
                "emojis_this_month": monthly_emotions_data,
                "emoji_counts": emoji_counts,
                "goals_info": goal_info,
                "high_priority_tasks": high_priority_tasks_data,
                "achieved_goals":  GoalSerializer(achieved_goals, many=True).data,
                "weekly_emotions":weekly_emotions_data,
                "ai_analytics":ai_analytics
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# the logic below, is needed because everytime the user navigate/refresh the dashboard the ai insights is regenerated
# which makes the loading longer, and unneccsary in terms of updating the insights since the user data havent changed

# so the logic here basically is:
# - first checks, did the user already have a response from ai stored in the AiAnalysisReport? if no then generate new one in the dashboard get method
#   otherwase, go in another checking statement, did the user check in today? if he didnt then just retrieve the stored info, no need to send to the llm
#   however, if the user chacked in today, then by calculating the time he checked in against when the report generated, the return would defer
#               - he checked in after the generation -> update and create new resposne
#               - he checked in before the generation -> just retrieve the stored info
def check_get_ai_submitted_report(user, date):
    ai_daily_report = AiAnalysisReport.objects.filter(user=user, date=date).order_by('-time_reported').first()
    if ai_daily_report:
        has_checked_in = Emotion.objects.filter(user=user, date=date).exists()

        if has_checked_in:
            time_he_checked_in = ai_daily_report.time_checked_in
            time_ai_generated_report = ai_daily_report.time_reported
            if time_he_checked_in > time_ai_generated_report:
                return False
            else:
                serializer = AiAnalysisReportSerilaizer(ai_daily_report)
                return serializer.data.get('ai_report')
        else:
            serializer = AiAnalysisReportSerilaizer(ai_daily_report)
            return serializer.data.get('ai_report')
    else:
        return False