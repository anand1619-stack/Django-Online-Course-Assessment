from django.db import models
from django.conf import settings


class Course(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Lesson(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons"
    )
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["order"]


class Question(models.Model):
    question_text = models.CharField(max_length=2000)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="questions"
    )
    grade = models.IntegerField(default=0)

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="choices"
    )
    choice_text = models.CharField(max_length=1000)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.choice_text


class Submission(models.Model):
    choices = models.ManyToManyField(Choice)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="exam_submissions"
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submission by {self.user}"

    def get_score(self):
        return sum(
            choice.question.grade
            for choice in self.choices.all()
            if choice.is_correct
        )
