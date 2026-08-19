from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from courses.models import Course, Enrollment
from .models import AttendanceSession, AttendanceRecord
from .forms import AttendanceSessionForm

@login_required
def session_create(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk, instructor=request.user)
    if request.method == "POST":
        form = AttendanceSessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False); session.course = course; session.save()
            for e in Enrollment.objects.filter(course=course):
                AttendanceRecord.objects.get_or_create(session=session, student=e.student, defaults={"status": "absent"})
            return redirect("mark_attendance", session_pk=session.pk)
    else:
        form = AttendanceSessionForm()
    return render(request, "attendance/session_form.html", {"form": form, "course": course})

@login_required
def mark_attendance(request, session_pk):
    session = get_object_or_404(AttendanceSession, pk=session_pk, course__instructor=request.user)
    records = session.records.select_related("student").order_by("student__first_name")
    if request.method == "POST":
        for record in records:
            record.status = request.POST.get(f"status_{record.pk}", "absent")
            record.save()
        messages.success(request, "Attendance saved!")
        return redirect("attendance_report", course_pk=session.course.pk)
    return render(request, "attendance/mark_attendance.html", {"session": session, "records": records})

@login_required
def attendance_report(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk, instructor=request.user)
    sessions = course.sessions.prefetch_related("records__student").order_by("date")
    report = []
    for e in Enrollment.objects.filter(course=course).select_related("student"):
        student = e.student
        row = {"student": student, "records": [session.records.filter(student=student).first() for session in sessions]}
        all_r = AttendanceRecord.objects.filter(student=student, session__course=course)
        row["total_present"] = all_r.filter(status="present").count()
        row["total_late"] = all_r.filter(status="late").count()
        row["total_absent"] = all_r.filter(status="absent").count()
        report.append(row)
    return render(request, "attendance/attendance_report.html", {"course": course, "sessions": sessions, "report": report})

@login_required
def my_attendance(request):
    data = []
    for e in Enrollment.objects.filter(student=request.user).select_related("course"):
        sessions = e.course.sessions.all()
        records = AttendanceRecord.objects.filter(student=request.user, session__course=e.course)
        total = sessions.count()
        present = records.filter(status="present").count()
        late = records.filter(status="late").count()
        data.append({
            "course": e.course, "total": total, "present": present, "late": late,
            "absent": records.filter(status="absent").count(),
            "percentage": round(((present+late)/total)*100,1) if total else 0,
            "records": records.select_related("session").order_by("session__date"),
        })
    return render(request, "attendance/my_attendance.html", {"attendance_data": data})
