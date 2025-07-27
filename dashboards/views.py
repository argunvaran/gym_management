from django.shortcuts import render, redirect, get_object_or_404
from .models import Lesson, Enrollment, LessonDay
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .forms import LessonForm
from django.contrib import messages
from django.db.models import Q, Count, F
from collections import defaultdict
from django.shortcuts import HttpResponseRedirect
from django.urls import reverse
from django.core.paginator import Paginator

@login_required
def lesson_list(request):
    lessons = Lesson.objects.all()
    lesson_days = LessonDay.objects.filter(lesson__in=lessons).order_by('date', 'start_time')
    return render(request, 'dashboards/lesson_list.html', {'lessons': lessons, 'lesson_days': lesson_days})

@login_required
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    enrollments = Enrollment.objects.filter(lesson=lesson, status='approved')
    approved_count = enrollments.count()
    max_students = lesson.max_students
    lesson_days = LessonDay.objects.filter(lesson=lesson).order_by('date', 'start_time')
    return render(request, 'dashboards/lesson_detail.html', {
        'lesson': lesson,
        'enrollments': enrollments,
        'approved_count': approved_count,
        'max_students': max_students,
        'lesson_days': lesson_days
    })

@login_required
def create_lesson(request):
    if request.user.is_teacher():
        if request.method == 'POST':
            form = LessonForm(request.POST)
            if form.is_valid():
                lesson = form.save(commit=False)
                lesson.teacher = request.user
                lesson.save()
                return redirect('teacher_dashboard')
        else:
            form = LessonForm()
        return render(request, 'dashboards/create_lesson.html', {'form': form})
    return HttpResponse("Only teachers can create lessons.")

@login_required
def enroll_in_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.user.is_student():
        enrollment, created = Enrollment.objects.get_or_create(lesson=lesson, student=request.user)
        if created:
            enrollment.status = 'requested'
            enrollment.save()
            messages.success(request, "Your request to join the lesson has been sent.")
        else:
            messages.info(request, "You have already requested to join this lesson.")
        return redirect('all_lessons')
    return HttpResponse("Only students can enroll in lessons.")

@login_required
def manage_enrollment(request, enrollment_id, action):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    if request.user == enrollment.lesson.teacher:
        if action == 'approve':
            enrollment.status = 'approved'
            enrollment.save()
            messages.success(request, f"{enrollment.student.username}'s request to join '{enrollment.lesson.title}' has been approved.")
        elif action == 'reject':
            enrollment.status = 'rejected'
            enrollment.save()
            messages.error(request, f"{enrollment.student.username}'s request to join '{enrollment.lesson.title}' has been rejected.")
        return redirect('teacher_dashboard')
    return HttpResponse("You are not authorized to manage this enrollment.")

@login_required
def teacher_dashboard(request):
    # Öğretmenin verdiği tüm dersleri alıyoruz
    lessons = Lesson.objects.filter(teacher=request.user)

    # Filtreleme parametreleri
    query = request.GET.get('query', '').strip()
    date_query = request.GET.get('date', '').strip()
    status_query = request.GET.get('status', '').strip()

    # Ders başlığı, öğretmen adı veya açıklamaya göre arama yapıyoruz
    if query:
        lessons = lessons.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query)
        )
    # Başlangıç tarihine göre arama
    if date_query:
        lessons = lessons.filter(start_date__date=date_query)

    # Duruma göre filtreleme
    if status_query:
        lessons = lessons.filter(enrollments__status=status_query)

    # Onay bekleyen ders başvurularını alıyoruz
    pending_enrollments = Enrollment.objects.filter(lesson__in=lessons, status='requested')

    # Sayfalama
    paginator = Paginator(lessons, 5)  # Sayfa başına 5 ders
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'dashboards/teacher_dashboard.html', {
        'page_obj': page_obj,
        'pending_enrollments': pending_enrollments,
        'query': query,
        'date_query': date_query,
        'status_query': status_query,
    })

@login_required
def all_lessons(request):
    lessons = Lesson.objects.none()  # İlk başta boş bir sorgu seti döndür

    # Filtreleme parametrelerini al
    query = request.GET.get('query', '').strip()
    date_query = request.GET.get('date', '').strip()

    # Eğer filtreleme parametrelerinden biri doluysa arama yap
    if query or date_query:
        lessons = Lesson.objects.all()  # Filtreleme yapacağımız tüm dersleri al

        if query:
            lessons = lessons.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(teacher__username__icontains=query)
            )

        if date_query:
            lessons = lessons.filter(start_date__date=date_query)

    # Sayfalama
    paginator = Paginator(lessons, 5)  # Sayfa başına 5 ders
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'dashboards/all_lessons.html', {
        'page_obj': page_obj,
        'query': query,
        'date_query': date_query,
    })

@login_required
def student_dashboard(request):
    # Öğrencinin etkileşime geçtiği tüm ders kayıtlarını alıyoruz
    enrollments = Enrollment.objects.filter(student=request.user)
    lessons = Lesson.objects.filter(id__in=[enrollment.lesson_id for enrollment in enrollments])

    # Öğrencinin her ders için durumunu saklayan bir sözlük oluşturuyoruz
    lesson_status = {enrollment.lesson_id: enrollment.status for enrollment in enrollments}

    # Arama parametrelerini alıyoruz
    query = request.GET.get('query', '').strip()
    date_query = request.GET.get('date', '').strip()
    status_query = request.GET.get('status', '').strip()

    # Ders başlığı, öğretmen adı veya açıklamaya göre arama yapıyoruz
    if query:
        lessons = lessons.filter(
            Q(teacher__username__icontains=query) | 
            Q(title__icontains=query) | 
            Q(description__icontains=query)
        )
    # Başlangıç tarihine göre arama
    if date_query:
        lessons = lessons.filter(start_date__date=date_query)

    # Duruma göre filtreleme
    if status_query:
        enrollments = enrollments.filter(status=status_query)
        lessons = Lesson.objects.filter(id__in=[enrollment.lesson_id for enrollment in enrollments])

    # Sayfalama
    paginator = Paginator(lessons, 5)  # Sayfa başına 5 ders
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'dashboards/student_dashboard.html', {
        'page_obj': page_obj,
        'query': query,
        'date_query': date_query,
        'status_query': status_query,
        'lesson_status': lesson_status  # Derslerin durumları
    })

@login_required
def request_enrollment(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.user.is_student():
        enrollment, created = Enrollment.objects.get_or_create(lesson=lesson, student=request.user)
        if created:
            enrollment.status = 'requested'
            enrollment.save()
            messages.success(request, f"You have requested to join '{lesson.title}'.")
        else:
            messages.info(request, "You have already requested to join this lesson.")
        
        # `available_lessons` sayfasına yönlendiriyoruz
        return HttpResponseRedirect(reverse('available_lessons'))
    else:
        return HttpResponse("Only students can request enrollment.")


@login_required
def available_lessons(request):
    if not request.user.is_student():
        return HttpResponse("Only students can view available lessons.")
    
    # Başlangıçta boş ders listesi
    lessons = Lesson.objects.none()

    # Arama sorgusu ve tarih filtresi
    query = request.GET.get('query', '').strip()
    date_query = request.GET.get('date', '').strip()

    # Öğrencinin daha önce başvurmadığı ve kapasitesi dolmamış dersleri filtreliyoruz
    student_enrollments = Enrollment.objects.filter(student=request.user).values_list('lesson_id', flat=True)
    lessons = Lesson.objects.exclude(id__in=student_enrollments) \
        .annotate(approved_count=Count('enrollments', filter=Q(enrollments__status='approved'))) \
        .filter(approved_count__lt=F('max_students'))

    # Ders başlığı, öğretmen veya açıklamaya göre arama
    if query:
        lessons = lessons.filter(
            Q(title__icontains=query) | 
            Q(teacher__username__icontains=query) | 
            Q(description__icontains=query)
        )
    # Tarih filtresi
    if date_query:
        lessons = lessons.filter(start_date__date=date_query)

    lessons = lessons.order_by('start_date')

    # Sayfalama
    paginator = Paginator(lessons, 5)  # Sayfa başına 5 ders
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'dashboards/available_lessons.html', {
        'page_obj': page_obj,
        'query': query,
        'date_query': date_query
    })