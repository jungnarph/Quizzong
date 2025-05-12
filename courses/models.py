from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import models
from django.forms import ValidationError
from django.utils import timezone
from django.utils.text import slugify

from datetime import timedelta
from taggit.managers import TaggableManager
from taggit.models import Tag

from .tags import SluggedTag, TaggedQuestion

import uuid

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_courses')
    students = models.ManyToManyField(User, related_name='enrolled_courses', through='CourseEnrollment')
    created_at = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return f"/courses/{self.id}/"
    
class CourseEnrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')

class CourseInvitation(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    inviter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invitations_sent')
    invitation_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def default_expiration():
        return timezone.now() + timedelta(hours=3)

    expiration_date = models.DateTimeField(default=default_expiration)


    def is_valid(self):
        return self.expiration_date > timezone.now()

    def get_invitation_url(self):
        # Generate the URL for the invitation using the unique invitation code
        return f"/courses/join/{self.invitation_code}/"

    def __str__(self):
        return f"Invitation for {self.course.title} from {self.inviter.username}"
    
class Quiz(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    course = models.ForeignKey(Course, related_name='quizzes', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    available_from = models.DateTimeField()
    available_until = models.DateTimeField()
    due_date = models.DateTimeField()
    time_limit = models.DurationField()

    publish = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')

    questions = models.ManyToManyField('Question', related_name='quizzes')

    class Meta():
        verbose_name = "Quiz"
        verbose_name_plural = "Quizzes"

    def __str__(self):
        return self.title

class Question(models.Model):
    SHORT = 'short'
    LONG = 'long'
    MC_SINGLE = 'mc_single'
    MC_MULTIPLE = 'mc_multiple'

    TYPES = [
        (SHORT, 'Short Answer'),
        (LONG, 'Long Answer'),
        (MC_SINGLE, 'Multiple Choice (Single Answer)'),
        (MC_MULTIPLE, 'Multiple Choice (Multiple Answers)'),
    ]

    course = models.ForeignKey(Course, related_name="questions", on_delete=models.CASCADE)
    owner = models.ForeignKey(User, related_name="questions", on_delete=models.CASCADE)
    text = models.TextField()
    type = models.CharField(max_length=20, choices=TYPES)
    points = models.PositiveIntegerField()
    order = models.PositiveIntegerField(default=0)

    correct_answer = models.TextField(blank=True, null=True)  # Used only for SHORT/LONG types
    tags = TaggableManager(through=TaggedQuestion, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.type in [self.MC_SINGLE, self.MC_MULTIPLE]:
            correct_options = self.options.filter(is_correct=True).count()

            if correct_options == 0:
                raise ValidationError("Multiple Choice questions must have at least one correct option.")

            if self.type == self.MC_SINGLE and correct_options > 1:
                raise ValidationError("Single-answer MCQs must have only one correct option.")

        elif self.type in [self.SHORT, self.LONG]:
            if not self.correct_answer:
                raise ValidationError("Short and Long answer questions must have a correct_answer.")
        
        if not self.pk and not self.tags.exists():
            raise ValidationError("Each question must have at least one tag.")

    def get_all_quiz_questions(self):
        return self.quiz.questions.all()
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Only apply this tagging logic if the question is already saved and has quizzes assigned
        for quiz in self.quizzes.all():
            quiz_tag = slugify(quiz.title)
            existing_tags = [slugify(tag) for tag in self.tags.names()]
            if quiz_tag not in existing_tags:
                self.tags.add(quiz_tag)

    def __str__(self):
        return f"{self.text[:50]} ({self.get_type_display()})"

class Option(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

# class QuizAttempt(models.Model):
#     quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     started_at = models.DateTimeField(auto_now_add=True)
#     submitted_at = models.DateTimeField(null=True, blank=True)
#     total_score = models.FloatField(default=0)

#     class Meta:
#         unique_together = ('quiz', 'user')

# class Answer(models.Model):
#     attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
#     question = models.ForeignKey(Question, on_delete=models.CASCADE)
#     selected_option = models.ForeignKey(Option, null=True, blank=True, on_delete=models.SET_NULL)  # For MCQ
#     text_answer = models.TextField(null=True, blank=True)  # For SHORT or LONG answers
#     is_correct = models.BooleanField(null=True)  # Can be null if manually checked
#     score = models.FloatField(default=0)


    

