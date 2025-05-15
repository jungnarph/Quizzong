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
        messages.error(request, "Unauthorized access.")
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
    if request.user != course.owner:
        messages.error(request, "Unauthorized access.")
        return redirect('course_detail', course_id=course.id)
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
    if request.user != course.owner:
        messages.error(request, "Unauthorized access.")
        return redirect('course_detail', course_id=course.id)
    
    quiz_form = QuizForm(request.POST or None, course=course)
    context = {
        "quiz_form": quiz_form,
    }
    if quiz_form.is_valid():
        quiz = quiz_form.save(commit=False)
        quiz.course_id = course_id
        quiz.save()
        quiz_form.save_m2m()  # Just in case other M2M fields exist
            
        return redirect('quiz_detail', course_id=course_id, quiz_id=quiz.id)

    return render(request, 'main/quizzes/create_update_quiz.html', context)

@login_required
def quiz_detail(request, course_id, quiz_id):
    
    course = get_object_or_404(Course, id=course_id)
    quiz = get_object_or_404(Quiz, id=quiz_id)
    context = {
        'course': course,
        'quiz': quiz,
    }
    return render(request, 'main/quizzes/quiz_detail.html', context)

@login_required
def update_quiz(request, course_id, quiz_id):
    pass

@login_required
def create_question(request, quiz_id=None, course_id=None):
    
    quiz = Quiz.objects.filter(pk=quiz_id).first() if quiz_id else None
    course = Course.objects.filter(pk=course_id).first() if course_id else None
    if request.user != course.owner:
            messages.error(request, "Unauthorized access.")
            return redirect('course_detail', course_id=course.id)
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.owner = request.user
            question.course = course
            print(f"Quiz added to course {course}")
            question.save()

            if quiz:
                question.quizzes.add(quiz)
            
            form.save_m2m()  # for tags

            if question.type == 'choice':
                correct_index = request.POST.get('correct_option')
                options = []
                for i in range(5):  # max 5 options
                    text = request.POST.get(f'option_text_{i}')
                    if text:
                        options.append(Option(
                            question=question,
                            text=text,
                            is_correct=(str(i) == correct_index)
                        ))
                Option.objects.bulk_create(options)

            return redirect('quiz_detail', quiz_id=quiz.pk, course_id=course.pk) if quiz else redirect('course_detail', course_id=course.pk)

    else:
        form = QuestionForm()

    return render(request, 'main/questions/create_question.html', {
        'form': form,
        'quiz': quiz,
        'course': course
    })

@login_required
def import_questions(request, course_id, quiz_id):
    
    course = get_object_or_404(Course, id=course_id)
    quiz = get_object_or_404(Quiz, id=quiz_id, course=course)
    if request.user != course.owner:
        messages.error(request, "Unauthorized access.")
        return redirect('course_detail', course_id=course.id)

    # Get all questions for this course not already in the quiz
    available_questions = Question.objects.filter(
        course=course
    ).exclude(
        quizzes=quiz
    )

    if request.method == 'POST':
        selected_ids = request.POST.getlist('question_ids')
        questions_to_add = Question.objects.filter(id__in=selected_ids)
        quiz.questions.add(*questions_to_add)
        return redirect('quiz_detail', course_id=course.id, quiz_id=quiz.id)

    context = {
        'course': course,
        'quiz': quiz,
        'available_questions': available_questions,
    }
    return render(request, 'main/questions/import_questions.html', context)

@login_required
def question_list(request, course_id):
    if request.user != course.owner:
        messages.error(request, "Unauthorized access.")
        return redirect('course_detail', course_id=course.id)
    course = get_object_or_404(Course, id=course_id)
    questions = Question.objects.filter(course=course)

    context = {
        'course': course,
        'questions': questions
    }

    return render(request, 'main/questions/question_list.html', context)