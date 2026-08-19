from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        INSTRUCTOR = "instructor", "Instructor"
        ADMIN = "admin", "Admin"

    SEMESTER_CHOICES = [(i, f"Semester {i}") for i in range(1, 9)]

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    student_id = models.CharField(max_length=50, blank=True, null=True, unique=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    semester = models.IntegerField(choices=SEMESTER_CHOICES, blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)

    @property
    def is_student(self): return self.role == self.Role.STUDENT
    @property
    def is_instructor(self): return self.role == self.Role.INSTRUCTOR
    @property
    def is_admin_role(self): return self.role == self.Role.ADMIN

    def get_semester_display_name(self):
        return f"Semester {self.semester}" if self.semester else "No semester assigned"

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"


class StudentRecord(models.Model):
    """
    Pre-loaded registry of valid student IDs imported from a CSV.
    When a student tries to sign up, their ID is checked against this table.
    Only students whose ID appears here and is marked active can create an account.
    This acts as a stand-in for a live school database connection.
    """
    student_id = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    department = models.CharField(max_length=100, blank=True)
    semester = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    imported_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_id} — {self.first_name} {self.last_name}"

    class Meta:
        ordering = ['student_id']
