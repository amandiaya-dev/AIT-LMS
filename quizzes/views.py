from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from courses.models import Course, Enrollment
from .models import Quiz, Question, QuizAttempt, QuizAnswer
from .forms import QuizForm, QuestionForm

@login_required
def quiz_create(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk, instructor=request.user)
    if request.method == "POST":
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False); quiz.course = course; quiz.save()
            return redirect("question_add", quiz_pk=quiz.pk)
    else:
        form = QuizForm()
    return render(request, "quizzes/quiz_form.html", {"form": form, "course": course})

@login_required
def question_add(request, quiz_pk):
    quiz = get_object_or_404(Quiz, pk=quiz_pk, course__instructor=request.user)
    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            q = form.save(commit=False); q.quiz = quiz; q.save()
            messages.success(request, "Question added!")
            return redirect("question_add", quiz_pk=quiz.pk)
    else:
        form = QuestionForm()
    return render(request, "quizzes/question_form.html", {"form": form, "quiz": quiz, "questions": quiz.questions.all()})

@login_required
def quiz_delete(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk, course__instructor=request.user)
    if request.method == "POST":
        course_pk = quiz.course.pk; title = quiz.title
        quiz.delete()
        messages.success(request, f'Quiz "{title}" deleted.')
        return redirect("course_detail", pk=course_pk)
    return render(request, "quizzes/quiz_confirm_delete.html", {"quiz": quiz})

@login_required
def quiz_attempts(request, quiz_pk):
    quiz = get_object_or_404(Quiz, pk=quiz_pk, course__instructor=request.user)
    return render(request, "quizzes/quiz_attempts.html", {"quiz": quiz, "attempts": quiz.attempts.select_related("student").order_by("-submitted_at")})

@login_required
def quiz_list(request):
    enrolled = Enrollment.objects.filter(student=request.user).values_list("course", flat=True)
    quizzes = Quiz.objects.filter(course__in=enrolled).select_related("course")
    attempted_ids = QuizAttempt.objects.filter(student=request.user).values_list("quiz_id", flat=True)
    return render(request, "quizzes/quiz_list.html", {"quizzes": quizzes, "attempted_ids": attempted_ids})

@login_required
def quiz_take(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    existing = QuizAttempt.objects.filter(student=request.user, quiz=quiz).first()
    if existing: return redirect("quiz_result", attempt_pk=existing.pk)
    questions = quiz.questions.all()
    if request.method == "POST":
        score = 0
        attempt = QuizAttempt.objects.create(quiz=quiz, student=request.user, score=0, total=questions.count())
        for q in questions:
            sel = request.POST.get(f"question_{q.pk}", "")
            if sel == q.correct_answer: score += 1
            QuizAnswer.objects.create(attempt=attempt, question=q, selected_option=sel)
        attempt.score = score; attempt.save()
        messages.success(request, f"Quiz submitted! Score: {score}/{questions.count()}")
        return redirect("quiz_result", attempt_pk=attempt.pk)
    return render(request, "quizzes/quiz_take.html", {"quiz": quiz, "questions": questions})

@login_required
def quiz_result(request, attempt_pk):
    attempt = get_object_or_404(QuizAttempt, pk=attempt_pk, student=request.user)
    return render(request, "quizzes/quiz_result.html", {"attempt": attempt, "answers": attempt.answers.select_related("question").all()})
