from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
# Create your models here.


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

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    content = models.TextField(max_length=100)
    date = models.DateField()
    priority = models.PositiveSmallIntegerField(max_length=1, choices=PRIORITY_CHOICES, default=2)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return self.content
    class Meta:
        ordering = ['-priority']
    
class Goal(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('achieved', 'Achieved'),
    )
    tasks = models.ManyToManyField(Task)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    content = models.TextField(max_length=150)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    year = models.PositiveIntegerField()

    def __str__(self):
        return self.content


class Emotion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emotions')
    emoji = models.CharField(max_length=10)
    feeling_text = models.TextField(max_length=300)
    ai_response = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.date} ({self.emoji})"

# TODO - determine the type of the excalidraw
# class VisionBoard(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vision_board')
#     excalidraw_data = 
