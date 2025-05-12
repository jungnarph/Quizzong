from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.urls import reverse
from .forms import CourseForm
from .forms import QuizForm, QuestionForm
from .models import Course, CourseEnrollment, CourseInvitation
from .models import Quiz, Question, Option

@login_required
def course_list(request):
    user = request.user

    enrolled_courses = user.enrolled_courses.exclude(owner=user)
    owned_courses = Course.objects.filter(owner=user)

    # Remove duplicates from the combined queryset
    courses = (enrolled_courses | owned_courses).distinct()

    context = {
        'courses': courses
    }

    return render(request, 'main/courses/course_list.html', context)

@login_required
def create_course(request):
    context = {'form': None}  # Initialize context with an empty 'form' key

    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.owner = request.user  # Set the course owner as the current user
            course.save()
            # Automatically enroll the creator
            course_enrollment, created = CourseEnrollment.objects.get_or_create(
                user=request.user,
                course=course,
                defaults={'enrolled_at': course.created_at}
            )
            messages.success(request, 'Course created successfully!')
            return redirect('course_list')  # Redirect to course list or wherever appropriate
        else:
            messages.error(request, 'There was an error creating the course. Please try again.')
    else:
        form = CourseForm()

    context['form'] = form  # Store the form in the context

    return render(request, 'main/courses/create_course.html', context)

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    is_owner = request.user == course.owner
    is_enrolled = CourseEnrollment.objects.filter(user=request.user, course=course).exists()
    invitation_code = request.session.pop('active_invitation_code', None)
    invitation = None

    if invitation_code and request.user == course.owner:
        invitation = get_object_or_404(CourseInvitation, invitation_code=invitation_code)


    context = {
        'course': course,
        'is_owner': is_owner,
        'is_enrolled': is_enrolled,
        'invitation': invitation,
    }

    return render(request, 'main/courses/course_detail.html', context)

@login_required
def get_course_invitation(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.user != course.owner:
        messages.error(request, "You are not authorized to invite users to this course.")
        return redirect('course_detail', course_id=course.id)

    # Check for an existing unexpired invitation
    invitation = CourseInvitation.objects.filter(
        course=course,
        inviter=request.user,
        expiration_date__gt=timezone.now()
    ).first()

    if not invitation:
        # No valid one found; create a new invitation
        invitation = CourseInvitation.objects.create(
            course=course,
            inviter=request.user,
        )

    # Pass the invitation code through the session
    request.session['active_invitation_code'] = str(invitation.invitation_code)

    return redirect('course_detail', course.id)

@login_required
def join_course_via_invitation(request, course_id, invitation_code):
    course = get_object_or_404(Course, id=course_id)
    try:
        invitation = CourseInvitation.objects.get(course=course, invitation_code=invitation_code)
    except CourseInvitation.DoesNotExist:
        return render(request, 'main/courses/invitation_invalid.html', {'course': course})


    if not invitation.is_valid():
        return render(request, 'main/courses/invitation_expired.html', {'course': course})

    if request.user == course.owner:
        return redirect('course_detail', course_id=course.id)

    if CourseEnrollment.objects.filter(user=request.user, course=course).exists():
        return redirect('course_detail', course_id=course.id)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'accept':
            CourseEnrollment.objects.create(user=request.user, course=course)
            messages.success(request, f"You've successfully joined the course {course.title}.")
            return redirect('course_detail', course_id=course.id)
        else:
            messages.info(request, "You declined the invitation.")
            return redirect('course_list')

    return render(request, 'main/invitations/invitation_prompt.html', {
        'course': course,
        'invitation': invitation
    })

@login_required
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.user != course.owner:
        messages.error(request, "You are not authorized to edit this course.")
        return redirect('course_detail', course_id=course.id)

    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully!')
            return redirect('course_detail', course_id=course.id)
    else:
        form = CourseForm(instance=course)

    context = {
        'form': form,
        'course': course
    }

    return render(request, 'main/courses/edit_course.html', context)

@login_required
def course_quiz_list(request, course_id):
    # Get the course using the provided course_id
    course = get_object_or_404(Course, id=course_id)
    
    # Fetch quizzes related to the course
    quizzes = Quiz.objects.filter(course=course)

    context = {
        'course': course,
        'quizzes': quizzes
    }
    
    return render(request, 'main/quizzes/course_quiz_list.html', context)

@login_required
def create_quiz(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    quiz_form = QuizForm(request.POST or None, course=course)
    QuestionFormset = modelformset_factory(Question, form=QuestionForm, extra=1)
    qs = Question.objects.none()
    question_formset = QuestionFormset(request.POST or None, queryset = qs)
    context = {
        "quiz_form": quiz_form,
        "question_formset": question_formset,
    }
    if all([quiz_form.is_valid(), question_formset.is_valid()]):
        quiz = quiz_form.save(commit=False)
        quiz.course_id = course_id
        quiz.save()
        quiz_form.save_m2m()  # Just in case other M2M fields exist

        # Save questions and add to quiz
        for question_form in question_formset:
            question = question_form.save(commit=False)
            question.course_id = course_id
            question.owner = request.user
            question.save()
            question_form.save_m2m()
            quiz.questions.add(question)  # <-- This links the question to the quiz
            
        return redirect('course_quiz_list', course_id=course_id)

    return render(request, 'main/quizzes/create_update_quiz.html', context)