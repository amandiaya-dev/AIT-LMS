from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.signup_view, name="signup"),
    path("signup/student/", views.student_signup_view, name="student_signup"),
    path("signup/instructor/", views.instructor_signup_view, name="instructor_signup"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("password/change/", views.change_password_view, name="change_password"),
    path("import-students/", views.import_students_view, name="import_students"),
    path("sample-csv/", views.sample_csv_view, name="sample_csv"),
    path("login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
