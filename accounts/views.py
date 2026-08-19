import csv
import io
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import StudentRecord
from .forms import StudentSignUpForm, InstructorSignUpForm, CustomPasswordChangeForm, CSVImportForm


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "accounts/signup_choice.html")


def student_signup_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                f'Welcome, {user.get_full_name()}! Your account has been created. '
                f'Your default password is AIT@2026 — please change it now.'
            )
            return redirect("change_password")
    else:
        form = StudentSignUpForm()
    return render(request, "accounts/student_signup.html", {"form": form})


def instructor_signup_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = InstructorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.get_full_name()}!')
            return redirect("dashboard")
    else:
        form = InstructorSignUpForm()
    return render(request, "accounts/instructor_signup.html", {"form": form})


@login_required
def change_password_view(request):
    if request.method == "POST":
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully!")
            return redirect("dashboard")
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, "accounts/change_password.html", {"form": form})


@login_required
def import_students_view(request):
    """
    Admin uploads a CSV file containing student records.
    The system reads each row and creates or updates a StudentRecord.
    Format: student_id, first_name, last_name, department, semester, status
    """
    if not request.user.is_staff and not request.user.is_admin_role:
        messages.error(request, "Only administrators can access this page.")
        return redirect("dashboard")

    results = None

    if request.method == "POST":
        form = CSVImportForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES["csv_file"]

            # Make sure it's a CSV
            if not csv_file.name.endswith(".csv"):
                messages.error(request, "Please upload a .csv file.")
                return redirect("import_students")

            data = csv_file.read().decode("utf-8")
            reader = csv.DictReader(io.StringIO(data))

            created = 0
            updated = 0
            skipped = 0
            errors = []

            for i, row in enumerate(reader, start=2):
                try:
                    student_id = row.get("student_id", "").strip()
                    first_name = row.get("first_name", "").strip()
                    last_name = row.get("last_name", "").strip()
                    department = row.get("department", "").strip()
                    semester_raw = row.get("semester", "").strip()
                    status = row.get("status", "active").strip().lower()

                    if not student_id or not first_name or not last_name:
                        errors.append(f"Row {i}: Missing required fields (student_id, first_name, last_name)")
                        skipped += 1
                        continue

                    semester = int(semester_raw) if semester_raw.isdigit() else None
                    is_active = status == "active"

                    record, was_created = StudentRecord.objects.update_or_create(
                        student_id=student_id,
                        defaults={
                            "first_name": first_name,
                            "last_name": last_name,
                            "department": department,
                            "semester": semester,
                            "is_active": is_active,
                        }
                    )
                    if was_created:
                        created += 1
                    else:
                        updated += 1

                except Exception as e:
                    errors.append(f"Row {i}: {str(e)}")
                    skipped += 1

            results = {
                "created": created,
                "updated": updated,
                "skipped": skipped,
                "errors": errors,
                "total": created + updated + skipped,
            }
            if created or updated:
                messages.success(
                    request,
                    f"Import complete: {created} new records added, {updated} updated, {skipped} skipped."
                )
    else:
        form = CSVImportForm()

    # Show current registry
    records = StudentRecord.objects.all().order_by("student_id")
    return render(request, "accounts/import_students.html", {
        "form": form,
        "records": records,
        "results": results,
    })


@login_required
def dashboard_view(request):
    context = {}

    if request.user.is_student:
        from courses.models import Enrollment, Course
        from assignments.models import Submission
        from quizzes.models import QuizAttempt

        enrollments = Enrollment.objects.filter(
            student=request.user
        ).select_related("course")
        enrolled_ids = enrollments.values_list("course_id", flat=True)
        recommended = Course.objects.filter(
            semester=request.user.semester,
            is_active=True
        ).exclude(id__in=enrolled_ids)

        context["enrollments"] = enrollments
        context["recommended"] = recommended
        context["submitted_count"] = Submission.objects.filter(student=request.user).count()
        context["quiz_attempts"] = QuizAttempt.objects.filter(student=request.user).count()

    elif request.user.is_instructor:
        from courses.models import Course
        from assignments.models import Assignment

        courses = Course.objects.filter(instructor=request.user)
        context["courses"] = courses
        context["total_students"] = sum(c.student_count() for c in courses)
        context["total_assignments"] = Assignment.objects.filter(
            course__instructor=request.user
        ).count()

    return render(request, "accounts/dashboard.html", context)


def sample_csv_view(request):
    """Let admin download a sample CSV template."""
    from django.http import HttpResponse
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="student_registry_template.csv"'
    writer = csv.writer(response)
    writer.writerow(["student_id", "first_name", "last_name", "department", "semester", "status"])
    writer.writerow(["AIT/2024/001", "Zaza", "Amadu", "Computer Science", "2", "active"])
    writer.writerow(["AIT/2024/002", "Kofi", "Mensah", "Engineering", "1", "active"])
    writer.writerow(["AIT/2024/003", "Ama", "Asante", "Business", "3", "active"])
    writer.writerow(["AIT/2024/004", "Ibrahim", "Bah", "Computer Science", "2", "inactive"])
    return response
