from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from courses.models import Course, Enrollment
from .models import Assignment, Submission
from .forms import AssignmentForm, SubmissionForm, GradeForm

@login_required
def assignment_create(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk, instructor=request.user)
    if request.method == "POST":
        form = AssignmentForm(request.POST)
        if form.is_valid():
            a = form.save(commit=False); a.course = course; a.save()
            messages.success(request, f'Assignment "{a.title}" posted!')
            return redirect("course_detail", pk=course.pk)
    else:
        form = AssignmentForm()
    return render(request, "assignments/assignment_form.html", {"form": form, "course": course, "action": "Post"})

@login_required
def submission_list(request, assignment_pk):
    assignment = get_object_or_404(Assignment, pk=assignment_pk, course__instructor=request.user)
    return render(request, "assignments/submission_list.html", {"assignment": assignment, "submissions": assignment.submissions.select_related("student")})

@login_required
def grade_submission(request, submission_pk):
    submission = get_object_or_404(Submission, pk=submission_pk, assignment__course__instructor=request.user)
    if request.method == "POST":
        form = GradeForm(request.POST, instance=submission)
        if form.is_valid():
            g = form.save(commit=False); g.graded_at = timezone.now(); g.save()
            messages.success(request, "Grade saved!")
            return redirect("submission_list", assignment_pk=submission.assignment.pk)
    else:
        form = GradeForm(instance=submission)
    return render(request, "assignments/grade_form.html", {"form": form, "submission": submission})

@login_required
def assignment_list(request):
    enrolled = Enrollment.objects.filter(student=request.user).values_list("course", flat=True)
    assignments = Assignment.objects.filter(course__in=enrolled).select_related("course").order_by("due_date")
    submitted_ids = Submission.objects.filter(student=request.user).values_list("assignment_id", flat=True)
    return render(request, "assignments/assignment_list.html", {"assignments": assignments, "submitted_ids": submitted_ids})

@login_required
def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    existing = Submission.objects.filter(student=request.user, assignment=assignment).first()
    if request.method == "POST" and not existing:
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            s = form.save(commit=False); s.assignment = assignment; s.student = request.user; s.save()
            messages.success(request, "Submitted!")
            return redirect("assignment_detail", pk=pk)
    else:
        form = SubmissionForm()
    return render(request, "assignments/assignment_detail.html", {"assignment": assignment, "form": form, "existing_submission": existing})
