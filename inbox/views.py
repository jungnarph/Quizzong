from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import Message
from .forms import MessageForm
from django.contrib.auth.decorators import login_required

# View for displaying the inbox
@login_required
def inbox(request):
    received_messages = Message.objects.filter(recipient=request.user).order_by('-timestamp')  # Use 'recipient' instead of 'receiver'
    return render(request, 'inbox/inbox.html', {'messages': received_messages})

# View for composing a message
@login_required
def compose(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            return redirect('inbox:inbox')  # Redirect to inbox after sending a message
    else:
        form = MessageForm()
    return render(request, 'inbox/compose.html', {'form': form})

# View for displaying a single message
@login_required
def message_detail(request, message_id):
    message = get_object_or_404(Message, pk=message_id)
    # Mark the message as read (if it hasn't been read already)
    if not message.read_at:
        message.read_at = message.timestamp  # Mark read time as the sent time
        message.save()
    return render(request, 'inbox/message_detail.html', {'message': message})

def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    
    # Ensure the message belongs to the current user (recipient)
    if message.recipient == request.user:
        message.delete()
    
    return redirect('inbox:inbox')  # Redirect back to the inbox