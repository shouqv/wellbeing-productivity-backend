from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()




    
class Goal(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('achieved', 'Achieved'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    content = models.TextField(max_length=150)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    year = models.PositiveIntegerField()

    def __str__(self):
        return self.content
    
    
class Task(models.Model):
    PRIORITY_CHOICES = (
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
    )

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    goals = models.ManyToManyField(Goal)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    content = models.TextField(max_length=100)
    date = models.DateField()
    priority = models.PositiveSmallIntegerField( choices=PRIORITY_CHOICES, default=2)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return self.content
    class Meta:
        ordering = ['-priority', '-status']

class Emotion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emotions')
    emoji = models.CharField(max_length=10)
    feeling_text = models.TextField(max_length=300)
    ai_response = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    # TODO : the below only for testing
    # date = models.DateField()

    def __str__(self):
        return f"{self.user.username} - {self.date} ({self.emoji})"



class VisionBoard(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vision_board')
    tldraw_data = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Vision Board"

#  the below model is mainly to store the ai reports, so that no extra request to the llm is created when dealing with the same data
#  will be used to genreate report based on each day and only if the user entered a new emotion
class AiAnalysisReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_name')
    ai_report = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    time_checked_in= models.DateTimeField(auto_now=True)
    time_reported=models.DateTimeField(auto_now_add=True)