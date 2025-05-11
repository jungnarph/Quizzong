from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('create/', views.create_course, name='create_course'),
    path('<int:course_id>/', views.course_detail, name='course_detail'),
    path('<int:course_id>/invite/', views.get_course_invitation, name='get_course_invitation'),
    path('<int:course_id>/join/<uuid:invitation_code>/', views.join_course_via_invitation, name='join_course'),
    path('<int:course_id>/edit/', views.edit_course, name='edit_course'),

    # path('<int:course_id>/members/', views.show_course_members, name='show_course_members'),
]