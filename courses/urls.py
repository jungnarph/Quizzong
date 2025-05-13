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

    path('<int:course_id>/quizzes/', views.course_quiz_list, name='course_quiz_list'),
    path('<int:course_id>/quizzes/create/', views.create_quiz, name='create_quiz'),
    path('<int:course_id>/quizzes/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('<int:course_id>/quizzes/<int:quiz_id>/edit/', views.update_quiz, name='update_quiz'),

    path('<int:course_id>/quizzes/<int:quiz_id>/questions/create/', views.create_question, name='quiz_create_question'),
    path('<int:course_id>/quizzes/<int:quiz_id>/questions/import/', views.import_question, name='quiz_import_question'),

    path('<int:course_id>/questions/create/', views.create_question, name='create_question'),

    path('secret/', views.show_option_list, name='show_option_list'),
]