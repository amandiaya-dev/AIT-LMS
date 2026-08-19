from django.urls import path
from . import views
urlpatterns = [
    path("", views.course_list, name="course_list"),
    path("create/", views.course_create, name="course_create"),
    path("<int:pk>/", views.course_detail, name="course_detail"),
    path("<int:pk>/enroll/", views.enroll, name="enroll"),
    path("<int:pk>/unenroll/", views.unenroll, name="unenroll"),
    path("<int:pk>/delete/", views.course_delete, name="course_delete"),
]
