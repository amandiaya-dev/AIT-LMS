from django.urls import path
from . import views
urlpatterns = [
    path("", views.assignment_list, name="assignment_list"),
    path("<int:pk>/", views.assignment_detail, name="assignment_detail"),
    path("course/<int:course_pk>/create/", views.assignment_create, name="assignment_create"),
    path("<int:assignment_pk>/submissions/", views.submission_list, name="submission_list"),
    path("submission/<int:submission_pk>/grade/", views.grade_submission, name="grade_submission"),
]
