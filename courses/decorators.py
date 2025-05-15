from functools import wraps
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Course

def course_owner_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, course_id, *args, **kwargs):
        course = get_object_or_404(Course, id=course_id)
        if request.user != course.owner:
            messages.error(request, "Unauthorized access.")
            return redirect('course_detail', course_id=course.id)
        return view_func(request, course_id, *args, **kwargs)
    return _wrapped_view

def ensure_course_owner(request, course):
    if course.owner != request.user:
        messages.error(request, "You are not authorized to access this course.")
        return False
    return True
