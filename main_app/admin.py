from django.contrib import admin
from .models import Goal , Task , Emotion

# Register your models here.
admin.site.register(Goal)
admin.site.register(Task)
admin.site.register(Emotion)