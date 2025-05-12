from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from .models import Question

@receiver(post_save, sender=Question)
def add_quiz_tag_on_create(sender, instance, created, **kwargs):
    if not created:
        return  # Exit early if not a newly created Question

    for quiz in instance.quizzes.all():
        quiz_tag = slugify(quiz.title)
        existing_tags = [slugify(tag) for tag in instance.tags.names()]
        if quiz_tag not in existing_tags:
            instance.tags.add(quiz_tag)