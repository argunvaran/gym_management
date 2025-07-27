from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path('user_management/', views.user_management, name='user_management'),
    path('user/create/', views.create_user, name='create_user'),
    path('user/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('skill/create/', views.create_skill, name='create_skill'),
    path('skill/edit/<int:skill_id>/', views.edit_skill, name='edit_skill'),
        
    path('', views.home, name='home'),

    path('teacher/lessons/', views.view_all_teacher_lessons, name='view_teacher_lessons'),
    path('teacher/<int:teacher_id>/lessons/', views.view_teacher_lessons, name='view_specific_teacher_lessons'),

    path('user/<int:user_id>/', views.user_detail, name='user_detail'),
]
