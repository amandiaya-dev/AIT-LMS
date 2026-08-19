from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Course, Enrollment
from .forms import CourseForm

@login_required
def course_list(request):
    if request.user.is_instructor:
        courses = Course.objects.filter(instructor=request.user)
    else:
        courses = Course.objects.filter(is_active=True)
    enrolled_ids = Enrollment.objects.filter(student=request.user).values_list("course_id", flat=True) if request.user.is_student else []
    return render(request, "courses/course_list.html", {"courses": courses, "enrolled_ids": enrolled_ids})

@login_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists() if request.user.is_student else False
    return render(request, "courses/course_detail.html", {"course": course, "is_enrolled": is_enrolled})

@login_required
def course_create(request):
    if not request.user.is_instructor:
        return redirect("course_list")
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            messages.success(request, f'Course "{course.title}" created!')
            return redirect("course_list")
    else:
        form = CourseForm()
    return render(request, "courses/course_form.html", {"form": form, "action": "Create"})

@login_required
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk, instructor=request.user)
    if request.method == "POST":
        title = course.title
        course.delete()
        messages.success(request, f'Course "{title}" deleted.')
        return redirect("course_list")
    return render(request, "courses/course_confirm_delete.html", {"course": course})

@login_required
def enroll(request, pk):
    if not request.user.is_student: return redirect("course_list")
    course = get_object_or_404(Course, pk=pk)
    _, created = Enrollment.objects.get_or_create(student=request.user, course=course)
    if created: messages.success(request, f'Enrolled in "{course.title}"!')
    return redirect("course_list")

@login_required
def unenroll(request, pk):
    course = get_object_or_404(Course, pk=pk)
    Enrollment.objects.filter(student=request.user, course=course).delete()
    messages.success(request, f'Unenrolled from "{course.title}".')
    return redirect("course_list")
