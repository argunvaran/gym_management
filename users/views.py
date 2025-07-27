from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import User, Skill
from .forms import UserRegisterForm, UserUpdateForm, SkillForm
from django.contrib import messages
from dashboards.models import Lesson, Enrollment
from django.db.models import Q
from datetime import datetime


def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your account has been created. You can now log in.")
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Kullanıcı rolüne göre yönlendirme
            if user.is_teacher():
                return redirect('teacher_dashboard')  # Öğretmen için
            elif user.is_student():
                return redirect('student_dashboard')  # Öğrenci için
            elif user.is_manager():
                return redirect('user_management')    # Yönetici için
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'users/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def user_management(request):
    query = request.GET.get('query', '').strip()  # Arama sorgusunu alıyoruz
    users = User.objects.all()

    # Eğer bir arama sorgusu varsa, isme göre filtreleme yapıyoruz
    if query:
        users = users.filter(username__icontains=query)

    return render(request, 'users/user_management.html', {
        'users': users,
        'query': query
    })

@login_required
def create_user(request):
    if request.user.is_manager():
        if request.method == 'POST':
            form = UserRegisterForm(request.POST)
            if form.is_valid():
                user = form.save()
                # Skills alanını kaydetme
                if user.is_teacher() and 'skills' in form.cleaned_data:
                    user.skills.set(form.cleaned_data['skills'])
                return redirect('user_management')
        else:
            form = UserRegisterForm()
        return render(request, 'users/create_user.html', {'form': form})
    else:
        return redirect('user_management')

@login_required
def edit_user(request, user_id):
    if request.user.is_manager():
        user = get_object_or_404(User, id=user_id)
        if request.method == 'POST':
            form = UserUpdateForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                if user.is_teacher():
                    user.skills.set(form.cleaned_data['skills'])
                return redirect('user_management')
        else:
            form = UserUpdateForm(instance=user)
        return render(request, 'users/edit_user.html', {'form': form, 'user': user})
    else:
        messages.error(request, "You are not authorized to edit users.")
        return redirect('home')

@login_required
def create_skill(request):
    if request.user.is_manager():
        if request.method == 'POST':
            form = SkillForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('user_management')
        else:
            form = SkillForm()
        return render(request, 'users/create_skill.html', {'form': form})
    else:
        return redirect('home')

@login_required
def edit_skill(request, skill_id):
    if request.user.is_manager():
        skill = get_object_or_404(Skill, id=skill_id)
        if request.method == 'POST':
            form = SkillForm(request.POST, instance=skill)
            if form.is_valid():
                form.save()
                return redirect('user_management')
        else:
            form = SkillForm(instance=skill)
        return render(request, 'users/edit_skill.html', {'form': form, 'skill': skill})
    else:
        return redirect('home')

@login_required
def view_all_teacher_lessons(request):
    if request.user.is_manager():
        # Filtreleme parametrelerini al
        query = request.GET.get('query', '').strip()
        date_query = request.GET.get('date', '').strip()

        # Tüm dersleri filtrele
        lessons = Lesson.objects.all()

        # Öğretmen adına ve derse göre arama
        if query:
            lessons = lessons.filter(
                Q(teacher__username__icontains=query) | 
                Q(title__icontains=query)
            )
        # Tarihe göre arama
        if date_query:
            try:
                date = datetime.strptime(date_query, "%Y-%m-%d").date()
                lessons = lessons.filter(start_date__date=date)
            except ValueError:
                messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
        
        return render(request, 'users/view_all_teacher_lessons.html', {
            'lessons': lessons,
            'query': query,
            'date_query': date_query,
        })
    else:
        messages.error(request, "You are not authorized to view all teacher lessons.")
        return redirect('home')


@login_required
def view_teacher_lessons(request, teacher_id):
    if request.user.is_manager():
        teacher = get_object_or_404(User, id=teacher_id, role='teacher')
        lessons = Lesson.objects.filter(teacher=teacher)

        return render(request, 'users/view_teacher_lessons.html', {
            'teacher': teacher,
            'lessons': lessons,
        })
    else:
        messages.error(request, "You are not authorized to view teacher lessons.")
        return redirect('home')

@login_required
def user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)

    # Kullanıcı öğretmense, yeteneklerini getiriyoruz
    skills = user.skills.all() if user.is_teacher() else None

    # Kullanıcı öğrenci ise tüm ders etkileşimlerini getiriyoruz
    lessons_interactions = None
    if user.is_student():
        enrollments = Enrollment.objects.filter(student=user)
        lessons_interactions = [(enrollment.lesson, enrollment.status) for enrollment in enrollments]

    # Kullanıcı öğretmense tüm verdiği dersleri getiriyoruz
    lessons_given = Lesson.objects.filter(teacher=user) if user.is_teacher() else None

    return render(request, 'users/user_detail.html', {
        'user_detail': user,
        'skills': skills,
        'lessons_interactions': lessons_interactions,
        'lessons_given': lessons_given,
    })