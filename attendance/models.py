from django.db import models
from django.conf import settings
from courses.models import Course

class AttendanceSession(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sessions")
    title = models.CharField(max_length=200)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.course.title} - {self.title}"

class AttendanceRecord(models.Model):
    STATUS_CHOICES = [("present","Present"),("absent","Absent"),("late","Late")]
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name="records")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="attendance_records")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="absent")
    class Meta: unique_together = ("session", "student")
