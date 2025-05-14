from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import Message
from .forms import MessageForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from courses.models import Course

@login_required
def inbox(request):
    received_messages = Message.objects.filter(recipient=request.user).order_by('-timestamp')
    return render(request, 'inbox/inbox.html', {'messages': received_messages})

@login_required
def compose(request):
    if request.method == 'POST':
        form = MessageForm(request.POST, user=request.user)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            return redirect('inbox:inbox')
    else:
        form = MessageForm(user=request.user)
    return render(request, 'inbox/compose.html', {'form': form})

@login_required
def message_detail(request, message_id):
    message = get_object_or_404(Message, pk=message_id)
    
    # Only the recipient marks it as read
    if message.recipient == request.user and not message.read_at:
        message.read_at = message.timestamp
        message.save()

    return render(request, 'inbox/message_detail.html', {'message': message})

@login_required
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    
    # If current user is the recipient
    if message.recipient == request.user:
        message.recipient = None  # Hide from recipient only
        message.save()
    # If current user is the sender
    elif message.sender == request.user:
        message.sender = None  # Hide from sender only
        message.save()

    # If both sender and recipient are None, delete permanently
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
