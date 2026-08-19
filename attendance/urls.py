from django.urls import path
from . import views
urlpatterns = [
    path("my/", views.my_attendance, name="my_attendance"),
    path("course/<int:course_pk>/session/create/", views.session_create, name="session_create"),
    path("session/<int:session_pk>/mark/", views.mark_attendance, name="mark_attendance"),
    path("course/<int:course_pk>/report/", views.attendance_report, name="attendance_report"),
]
