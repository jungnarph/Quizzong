from django.urls import path
from . import views

app_name = 'inbox'

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('compose/', views.compose, name='compose'),
    path('message/<int:message_id>/', views.message_detail, name='message_detail'),
    path('message/<int:message_id>/delete/', views.delete_message, name='delete_message'),
    path('sent/', views.sent_messages, name='sent_messages'),  # ✅ new route
    path('load-recipients/', views.load_recipients, name='load_recipients'),
]
