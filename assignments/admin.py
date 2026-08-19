from django.contrib import admin
from .models import Assignment, Submission
@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "due_date")
@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("student", "assignment", "submitted_at", "score", "max_score")
