from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import Message
from .forms import MessageForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from courses.models import Course
from .gemini import check_profanity
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

@login_required
def inbox(request):
    received_messages = Message.objects.filter(
        recipient=request.user
    ).exclude(recipient=None).order_by('-timestamp')

    # Always pass compose form so modal can render on the same page
    compose_form = MessageForm(user=request.user)

    return render(request, 'inbox/inbox.html', {
        'messages': received_messages,
        'compose_form': compose_form,
    })
@login_required
def compose(request):
    if request.method == 'POST':
        form = MessageForm(request.POST, user=request.user)
        if form.is_valid():
            message_content = form.cleaned_data['body']

            # Check for profanity using Gemini
            if check_profanity(message_content):
                admin_user = User.objects.filter(username='admin').first()

                if admin_user:
                    warning_message = Message(
                        sender=admin_user,
                        recipient=request.user,
                        subject="Warning: Profanity Detected",
                        body="Your message contains profanity and was not sent. Please revise your message.",
                        timestamp=timezone.now()
                    )
                    warning_message.save()

                return render(request, 'inbox/warning.html')

            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            return redirect('inbox:inbox')
    else:
        form = MessageForm(user=request.user)

    return render(request, 'inbox/compose.html', {'form': form})

@login_required
def warning(request):
    return render(request, 'inbox/warning.html')

@login_required
def message_detail(request, message_id):
    message = get_object_or_404(Message, pk=message_id)

    # Mark as read if user is recipient and not already read
    if request.user == message.recipient and message.read_at is None:
        message.read_at = timezone.now()
        message.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'inbox/message_detail_partial.html', {'message': message})

    return render(request, 'inbox/message_detail.html', {'message': message})

@login_required
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)

    if request.user == message.recipient:
        message.recipient = None
        message.save()
    elif request.user == message.sender:
        message.sender = None
        message.save()

    if message.sender is None and message.recipient is None:
        message.delete()

    return redirect('inbox:inbox')

@login_required
def sent_messages(request):
    sent_messages = Message.objects.filter(sender=request.user).order_by('-timestamp')
    return render(request, 'inbox/sent_messages.html', {'messages': sent_messages})

@login_required
def load_recipients(request):
    course_id = request.GET.get('course_id')
    recipients = []
    if course_id:
        try:
            course = Course.objects.get(id=course_id)
            recipients = course.students.exclude(id=request.user.id).values('id', 'username')
        except Course.DoesNotExist:
            pass
    return JsonResponse(list(recipients), safe=False)

@login_required
def filter_messages(request):
    filter_type = request.GET.get('type', 'all')
    user = request.user

    if filter_type == 'sent':
        messages = Message.objects.filter(sender=user).order_by('-timestamp')
    elif filter_type == 'unread':
        messages = Message.objects.filter(recipient=user, read_at__isnull=True).order_by('-timestamp')
    else:
        messages = Message.objects.filter(recipient=user).order_by('-timestamp')

    return render(request, 'inbox/message_list_partial.html', {'messages': messages})

@login_required
@csrf_exempt  # Prefer to use CSRF token in JS, but here is fallback
def mark_read(request, message_id):
    if request.method == 'POST':
        try:
            message = Message.objects.get(pk=message_id, recipient=request.user)
            if message.read_at is None:
                message.read_at = timezone.now()
                message.save()
            return JsonResponse({'status': 'ok'})
        except Message.DoesNotExist:
            return JsonResponse({'status': 'not found'}, status=404)
    return JsonResponse({'status': 'invalid method'}, status=400)