from django.urls import path
from . import views

urlpatterns = [
    path('lessons/', views.lesson_list, name='lesson_list'),
    path('lessons/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('lessons/create/', views.create_lesson, name='create_lesson'),
    path('lessons/<int:lesson_id>/enroll/', views.enroll_in_lesson, name='enroll_in_lesson'),
    path('enrollment/<int:enrollment_id>/<str:action>/', views.manage_enrollment, name='manage_enrollment'),

    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    
    path('teacher_dashboard/', views.teacher_dashboard, name='teacher_dashboard'),

    path('all_lessons/', views.all_lessons, name='all_lessons'),
    path('lessons/<int:lesson_id>/request/', views.request_enrollment, name='request_enrollment'),
    
    path('available_lessons/', views.available_lessons, name='available_lessons'),
]
