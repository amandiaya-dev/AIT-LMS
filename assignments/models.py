from django.db import models
from django.conf import settings
from courses.models import Course

class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="assignments")
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.title} ({self.course.title})"

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submissions")
    text = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to="submissions/", blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    score = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    max_score = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)
    graded_at = models.DateTimeField(blank=True, null=True)
    class Meta: unique_together = ("assignment", "student")
    @property
    def grade_display(self):
        if self.score is not None and self.max_score:
            return f"{self.score}/{self.max_score} ({(self.score/self.max_score)*100:.1f}%)"
        return None
