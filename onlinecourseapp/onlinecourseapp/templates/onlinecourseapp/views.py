from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction

from .models import Course, Lesson, Question, Choice, Submission


@login_required
def submit(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)

    if request.method != "POST":
        return redirect("course_details", course_id=lesson.course.id)

    questions = Question.objects.filter(
        course=lesson.course
    )

    selected_choices = []

    for question in questions:
        choice_id = request.POST.get(str(question.id))

        if choice_id:
            choice = get_object_or_404(
                Choice,
                id=choice_id,
                question=question
            )
            selected_choices.append(choice)

    with transaction.atomic():
        submission = Submission.objects.create(
            user=request.user
        )
        submission.choices.set(selected_choices)

    return redirect(
        "show_exam_result",
        submission_id=submission.id
    )


@login_required
def show_exam_result(request, submission_id):
    submission = get_object_or_404(
        Submission,
        id=submission_id,
        user=request.user
    )

    questions = Question.objects.filter(
        choices__in=submission.choices.all()
    ).distinct()

    results = []
    score = 0
    correct_answers = 0

    for question in questions:
        selected = submission.choices.filter(
            question=question
        ).first()

        correct = selected is not None and selected.is_correct

        if correct:
            score += question.grade
            correct_answers += 1

        results.append({
            "question": question,
            "selected": selected,
            "correct": correct,
        })

    total_questions = questions.count()

    percentage = (
        correct_answers / total_questions * 100
        if total_questions else 0
    )

    return render(
        request,
        "exam_result.html",
        {
            "submission": submission,
            "results": results,
            "score": score,
            "correct_answers": correct_answers,
            "total_questions": total_questions,
            "percentage": percentage,
            "passed": percentage >= 70,
        }
    )
