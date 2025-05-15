from django.urls import path
from . import views

app_name = 'inbox'

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('compose/', views.compose, name='compose'),
    path('message/<int:message_id>/', views.message_detail, name='message_detail'),
    path('message/<int:message_id>/delete/', views.delete_message, name='delete_message'),
    path('sent/', views.sent_messages, name='sent_messages'),
    path('load-recipients/', views.load_recipients, name='load_recipients'),
    path('warning/', views.warning, name='warning'),
    path('filter/', views.filter_messages, name='filter_messages'),
    path('mark-read/<int:message_id>/', views.mark_read, name='mark_read'),
]
