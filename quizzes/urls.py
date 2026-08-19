from django.urls import path
from . import views
urlpatterns = [
    path("", views.quiz_list, name="quiz_list"),
    path("course/<int:course_pk>/create/", views.quiz_create, name="quiz_create"),
    path("<int:pk>/take/", views.quiz_take, name="quiz_take"),
    path("<int:pk>/delete/", views.quiz_delete, name="quiz_delete"),
    path("<int:quiz_pk>/questions/add/", views.question_add, name="question_add"),
    path("<int:quiz_pk>/attempts/", views.quiz_attempts, name="quiz_attempts"),
    path("result/<int:attempt_pk>/", views.quiz_result, name="quiz_result"),
]
