from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from datetime import timedelta, datetime


class Lesson(models.Model):
    LESSON_TYPE_CHOICES = (
        ('private', 'Private'),
        ('group', 'Group'),
    )
    
    title = models.CharField(max_length=100)
    description = models.TextField()
    lesson_type = models.CharField(max_length=10, choices=LESSON_TYPE_CHOICES)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lessons')
    max_students = models.PositiveIntegerField()
    duration_weeks = models.PositiveIntegerField()
    duration_hours = models.PositiveIntegerField()  # Ders süresi saat cinsinden
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)  # End date otomatik hesaplanacak

    def clean(self):
        # "Private" tipi dersler için max_students = 1 zorunluluğu
        if self.lesson_type == 'private':
            self.max_students = 1
        elif self.lesson_type == 'group' and self.max_students < 2:
            raise ValidationError("Group lessons must allow at least 2 students.")
        
        # Aynı başlıkta bir ders olup olmadığını kontrol et
        if Lesson.objects.filter(title=self.title).exclude(id=self.id).exists():
            raise ValidationError("A lesson with this title already exists. Please choose a different title.")

    def save(self, *args, **kwargs):
        # Temizleme işlemi ile doğrulamayı gerçekleştir
        self.clean()
        
        # Ders bitiş tarihini otomatik hesapla
        self.end_date = self.start_date + timedelta(weeks=self.duration_weeks)
        
        # Ders günleri ve saatlerini oluşturma
        super().save(*args, **kwargs)
        self.create_lesson_schedule()

    def create_lesson_schedule(self):
        # Önceki kayıtlı ders günlerini temizleyin
        self.lesson_days.all().delete()

        # Her hafta için ders günlerini oluştur
        for week in range(self.duration_weeks):
            lesson_date = self.start_date + timedelta(weeks=week)
            LessonDay.objects.create(
                lesson=self,
                date=lesson_date,
                start_time=lesson_date.time(),
                end_time=(lesson_date + timedelta(hours=self.duration_hours)).time()
            )

    def __str__(self):
        return self.title

class LessonDay(models.Model):
    lesson = models.ForeignKey(Lesson, related_name="lesson_days", on_delete=models.CASCADE)
    date = models.DateField()  # Ders tarihi
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.lesson.title} on {self.date} from {self.start_time} to {self.end_time}"

class Enrollment(models.Model):
    STATUS_CHOICES = (
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='enrollments')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='requested')

    class Meta:
        unique_together = ('lesson', 'student')
